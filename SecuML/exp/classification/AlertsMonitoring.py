# SecuML
# Copyright (C) 2016-2018  ANSSI
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

import os.path as path

from SecuML.core.classification.ClassifierDatasets import ClassifierDatasets
from SecuML.core.classification.conf.hyperparam_conf.HyperparamOptimConf \
        import HyperparamOptimConf
from SecuML.core.classification.conf.hyperparam_conf.RocAucConf \
        import RocAucConf
from SecuML.core.classification.conf.LogisticRegressionConf \
        import LogisticRegressionConf
from SecuML.core.data import labels_tools
from SecuML.core.tools import matrix_tools

from SecuML.exp.clustering.ClusteringConf import ClusteringConf
from SecuML.exp.clustering.ClusteringExperiment \
        import ClusteringExperiment
from SecuML.exp.conf.FeaturesConf import FeaturesConf
from SecuML.exp.db_tables import AlertsClusteringExpAlchemy


class AlertsMonitoring(object):

    def __init__(self, diadem_exp, datasets, predictions_monitoring):
        self.diadem_exp = diadem_exp
        self.datasets = datasets
        self.alerts_conf = diadem_exp.exp_conf.core_conf.test_conf.alerts_conf
        self.alerts = self.extractAlerts(predictions_monitoring)

    def groupAlerts(self):
        alerts_ids = self.alerts.index
        if len(alerts_ids) == 0:
            self.alerts_grouping_exp = None
        else:
            families = self.datasets.train_instances.annotations.getFamilies()
            num_families = len(set(families))
            if num_families > 1:
                self.alerts_grouping_exp = self.classifyAlerts(alerts_ids)
            else:
                self.alerts_grouping_exp = self.clusterAlerts(alerts_ids)
            # Add the clustering exp to the table AlertsClusteringExpAlchemy
            alerts_db = AlertsClusteringExpAlchemy(
                           diadem_id=self.diadem_exp.experiment_id,
                           clustering_id=self.alerts_grouping_exp.experiment_id)
            self.diadem_exp.session.add(alerts_db)
            self.diadem_exp.session.flush()

    def export(self, output_directory):
        self.exportRawAlerts(output_directory)

    def exportRawAlerts(self, directory):
        with open(path.join(directory, 'alerts.csv'), 'w') as f:
            self.alerts.to_csv(f, index_label='instance_id')

    def clusterAlerts(self, alerts_ids):
        self.checkNumClustersValidity(alerts_ids)
        core_clustering_conf = self.alerts_conf.clustering_conf
        clustering_exp = self.createClusteringExp(core_clustering_conf)
        instances = self.datasets.test_instances.getInstancesFromIds(alerts_ids)
        clustering_exp.run(instances=instances, quick=True)
        return clustering_exp

    def classifyAlerts(self, alerts_ids):
        model = self.getMulticlassModel()
        datasets = self.getMulticlassDatasets(model, alerts_ids)
        model.trainTestValidation(datasets)
        all_families = list(model.class_labels)
        predicted_families = model.testing_monitoring.getPredictedLabels()
        predicted_families = [all_families.index(x) for x in predicted_families]
        clustering_exp = self.createClusteringExp(None)
        clustering_exp.set_clusters(datasets.test_instances, predicted_families,
                                    None, None, False, all_families)
        return clustering_exp

    def createClusteringExp(self, core_clustering_conf):
        exp_conf = self.diadem_exp.exp_conf
        features_conf = FeaturesConf(exp_conf.features_conf.input_features,
                                     exp_conf.secuml_conf.logger)
        if self.diadem_exp.test_exp is not None:
            dataset_conf = exp_conf.test_exp_conf.dataset_conf
            annotations_conf = exp_conf.test_exp_conf.annotations_conf
        else:
            dataset_conf = exp_conf.dataset_conf
            annotations_conf = exp_conf.annotations_conf
        clustering_exp_conf = ClusteringConf(exp_conf.secuml_conf,
                                             dataset_conf,
                                             features_conf,
                                             annotations_conf,
                                             core_clustering_conf,
                                             experiment_name=None,
                                             parent=self.diadem_exp.experiment_id)
        return ClusteringExperiment(clustering_exp_conf, create=True,
                                    session=self.diadem_exp.session)


    def getMulticlassModel(self):
        logger = self.alerts_conf.logger
        hyperparam_conf = HyperparamOptimConf(4, 1, RocAucConf(logger), logger)
        core_conf = LogisticRegressionConf(False, True, 'liblinear',
                                           hyperparam_conf, logger)
        return core_conf.model_class(core_conf)

    def getMulticlassDatasets(self, model, alerts_ids):
        datasets = ClassifierDatasets(None, model.conf.sample_weight)
        train_instances = self.datasets.train_instances.getAnnotatedInstances(
                                                label=labels_tools.MALICIOUS)
        test_instances = self.datasets.test_instances.getInstancesFromIds(
                                                alerts_ids)
        datasets.setDatasets(train_instances, test_instances, None)
        return datasets

    def checkNumClustersValidity(self, alerts_ids):
        num_clusters = self.alerts_conf.clustering_conf.num_clusters
        num_alerts = len(alerts_ids)
        if num_alerts < num_clusters:
            self.alerts_conf.logger.warning(
                    'Cannot build %d clusters from %d alerts. '
                    'num_clusters should be smaller than num_alerts.'
                    % (num_clusters, num_alerts))
            num_clusters = min(num_alerts, 4)
            self.alerts_conf.clustering_conf.num_clusters = num_clusters
            self.alerts_conf.logger.warn('The number of clusters is set to %s'
                                         % (num_clusters))

    def extractAlerts(self, predictions_monitoring):
        detection_threshold = self.alerts_conf.detection_threshold
        alerts = matrix_tools.extract_rows_with_thresholds(
                            predictions_monitoring.predictions,
                            detection_threshold, None,
                            'predicted_proba')
        alerts = matrix_tools.sort_data_frame(alerts, 'predicted_proba', False,
                                            False)
        return alerts
