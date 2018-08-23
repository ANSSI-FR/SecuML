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

from SecuML.core.Classification.ClassifierDatasets import ClassifierDatasets
from SecuML.core.Classification.Configuration.TestConfiguration.UnlabeledLabeledConf \
        import UnlabeledLabeledConf
from SecuML.core.Classification.Configuration import ClassifierConfFactory
from SecuML.core.Clustering.Clustering import Clustering
from SecuML.core.Data import labels_tools
from SecuML.core.Tools import matrix_tools


class AlertsMonitoring(object):

    def __init__(self, datasets, predictions_monitoring, alerts_conf):
        self.datasets = datasets
        self.alerts_conf = alerts_conf
        self.alerts = self.extractAlerts(predictions_monitoring)

    def groupAlerts(self):
        alerts_ids = self.alerts.index
        if len(alerts_ids) == 0:
            self.alerts_grouping = None
        else:
            num_families = len(set(
                self.datasets.train_instances.annotations.getFamilies()))
            has_families = num_families > 1
            if has_families:
                self.alerts_grouping = self.classifyAlerts(alerts_ids)
            else:
                self.alerts_grouping = self.clusterAlerts(alerts_ids)

    def export(self, output_directory):
        self.exportRawAlerts(output_directory)
        self.exportAlertsGrouping(output_directory)

    def exportRawAlerts(self, directory):
        with open(path.join(directory, 'alerts.csv'), 'w') as f:
            self.alerts.to_csv(f, index_label='instance_id')

    def exportAlertsGrouping(self, directory):
        if self.alerts_grouping is None:
            return
        self.alerts_grouping.export(directory,
                                    drop_annotated_instances=False)

    def clusterAlerts(self, alerts_ids):
        self.checkNumClustersValidity(alerts_ids)
        clustering_conf = self.alerts_conf.clustering_conf
        instances = self.datasets.test_instances.getInstancesFromIds(
            alerts_ids)
        clustering_algo = clustering_conf.algo(instances, clustering_conf)
        clustering_algo.fit()
        clustering_algo.generateClustering(drop_annotated_instances=False)
        return clustering_algo.clustering

    def classifyAlerts(self, alerts_ids):
        model = self.getMulticlassModel()
        datasets = self.getMulticlassDatasets(model, alerts_ids)
        model.trainTestValidation(datasets)
        all_families = list(model.class_labels)
        predicted_families = model.testing_monitoring.getPredictedLabels()
        predicted_families = [all_families.index(
            x) for x in predicted_families]
        clustering = Clustering(datasets.test_instances, predicted_families)
        clustering.generateClustering(None, None,
                                      drop_annotated_instances=False,
                                      cluster_labels=all_families)
        return clustering

    def getMulticlassModel(self):
        params = {}
        params['num_folds'] = 4
        params['sample_weight'] = False
        params['families_supervision'] = True
        params['optim_algo'] = 'liblinear'
        params['alerts_conf'] = None
        test_conf = UnlabeledLabeledConf(logger=self.alerts_conf.logger)
        params['test_conf'] = test_conf
        conf = ClassifierConfFactory.getFactory().fromParam(
                        'LogisticRegression',
                        params,
                        logger=self.alerts_conf.logger)
        model = conf.model_class(conf)
        return model

    def getMulticlassDatasets(self, model, alerts_ids):
        datasets = ClassifierDatasets(None, model.conf.sample_weight)
        train_instances = self.datasets.train_instances.getAnnotatedInstances(
            label=labels_tools.MALICIOUS)
        test_instances = self.datasets.test_instances.getInstancesFromIds(
            alerts_ids)
        datasets.setDatasets(train_instances, test_instances)
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
        alerts = matrix_tools.extractRowsWithThresholds(
            predictions_monitoring.predictions,
            detection_threshold, None,
            'predicted_proba')
        alerts = matrix_tools.sortDataFrame(
            alerts, 'predicted_proba', False, False)
        return alerts
