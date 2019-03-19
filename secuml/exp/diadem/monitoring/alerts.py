# SecuML
# Copyright (C) 2016-2019  ANSSI
#
# SecuML is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# SecuML is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with SecuML. If not, see <http://www.gnu.org/licenses/>.

from secuml.core.classif.conf.classifiers.logistic_regression \
        import LogisticRegressionConf
from secuml.core.classif.conf.hyperparam import HyperparamConf
from secuml.core.data.labels_tools import MALICIOUS

from secuml.exp import experiment
from secuml.exp.clustering.conf import ClusteringConf
from secuml.exp.tools.db_tables import DiademExpAlchemy
from secuml.exp.tools.db_tables import ExpAlchemy
from secuml.exp.tools.db_tables import ExpRelationshipsAlchemy
from secuml.exp.diadem.alerts_clustering import AlertsClusteringExp


class AlertsMonitoring(object):

    def __init__(self, test_exp, alerts_conf):
        self.test_exp = test_exp
        self.alerts_conf = alerts_conf

    def extract(self, predictions):
        threshold = self.alerts_conf.detection_threshold
        self.alerts = predictions.get_alerts(threshold)

    def group(self):
        alerts_ids = [alert.instance_id for alert in self.alerts]
        if len(alerts_ids) == 0:
            return
        train_instances, alerts_instances = self._get_datasets(alerts_ids)
        families = train_instances.annotations.get_families()
        num_families = len(set(families))
        if num_families > 1:
            self._classify(alerts_instances, train_instances)
        else:
            self._cluster(alerts_instances)

    def display(self, output_dir):
        return

    def _cluster(self, alerts_instances):
        self._check_num_clusters(alerts_instances)
        core_clustering_conf = self.alerts_conf.clustering_conf
        clustering_exp = self._create_clustering_exp(core_clustering_conf)
        clustering_exp.run(instances=alerts_instances, quick=True)

    def _classify(self, alerts_instances, train_instances):
        model = self._train_multiclass(train_instances)
        predict_families, all_families = self._predict_families(
                                                              model,
                                                              alerts_instances)
        clustering_exp = self._create_clustering_exp(None)
        clustering_exp.set_clusters(alerts_instances, predict_families,
                                    None, False, all_families)

    def _predict_families(self, model, alerts_instances):
        predicted_families, _ = model.testing(alerts_instances)
        all_families = list(model.class_labels)
        predicted_families = [all_families.index(x)
                              for x in predicted_families.values]
        return predicted_families, all_families

    def _create_clustering_exp(self, core_clustering_conf):
        exp_conf = self.test_exp.exp_conf
        conf = ClusteringConf(exp_conf.secuml_conf,
                              exp_conf.dataset_conf,
                              exp_conf.features_conf,
                              exp_conf.annotations_conf,
                              core_clustering_conf,
                              name='Alerts_%i' % exp_conf.exp_id,
                              parent=exp_conf.exp_id)
        return AlertsClusteringExp(conf, self.test_exp.exp_conf.parent,
                                   create=True, session=self.test_exp.session)

    def _train_multiclass(self, train_instances):
        # Multi-class model
        num_folds = None
        n_jobs = None
        hyperparam_conf = self.test_exp.classifier.conf.hyperparam_conf
        if hyperparam_conf is not None:
            optim_conf = hyperparam_conf.optim_conf
            if optim_conf is not None:
                num_folds = optim_conf.num_folds
                n_jobs = optim_conf.n_jobs
        hyperparam_conf = HyperparamConf.get_default(
                                   num_folds, n_jobs, True,
                                   LogisticRegressionConf._get_hyper_desc(),
                                   self.alerts_conf.logger)
        core_conf = LogisticRegressionConf(True, 'liblinear', hyperparam_conf,
                                           self.alerts_conf.logger)
        model = core_conf.model_class(core_conf)
        # Training
        model.training(train_instances)
        return model

    def _check_num_clusters(self, alerts_instances):
        num_clusters = self.alerts_conf.clustering_conf.num_clusters
        num_alerts = alerts_instances.num_instances()
        if num_alerts < num_clusters:
            self.alerts_conf.logger.warning(
                    'Cannot build %d clusters from %d alerts. '
                    'num_clusters should be smaller than num_alerts.'
                    % (num_clusters, num_alerts))
            num_clusters = min(num_alerts, 4)
            self.alerts_conf.clustering_conf.num_clusters = num_clusters
            self.alerts_conf.logger.warn('The number of clusters is set to %s'
                                         % (num_clusters))

    def _get_datasets(self, alerts_ids):
        # alerts_instances
        test_instances = self.test_exp.test_instances
        alerts_instances = test_instances.get_from_ids(alerts_ids)
        # train_instances loaded from the Train experiment.
        diadem_id = self.test_exp.exp_conf.parent
        query = self.test_exp.session.query(DiademExpAlchemy)
        query = query.join(DiademExpAlchemy.exp)
        query = query.join(ExpAlchemy.parents)
        query = query.filter(DiademExpAlchemy.type == 'train')
        query = query.filter(ExpAlchemy.kind == 'Detection')
        query = query.filter(ExpRelationshipsAlchemy.parent_id == diadem_id)
        train_exp_id = query.one().exp_id
        exp = experiment.get_factory().from_exp_id(
                                         train_exp_id,
                                         self.test_exp.exp_conf.secuml_conf,
                                         self.test_exp.session)
        train_instances = exp.get_instances().get_annotated_instances(
                                                            label=MALICIOUS)
        return train_instances, alerts_instances
