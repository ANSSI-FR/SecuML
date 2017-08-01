## SecuML
## Copyright (C) 2016-2017  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

import json
import warnings

from SecuML.Classification.ClassifierDatasets import ClassifierDatasets
from SecuML.Classification.Configuration.TestConfiguration import TestConfiguration
from SecuML.Classification.Configuration import ClassifierConfFactory
from SecuML.Clustering.Configuration.ClusteringConfiguration import ClusteringConfiguration
from SecuML.Clustering.Clustering import Clustering
from SecuML.Data import labels_tools
from SecuML.Experiment.ClassificationExperiment import ClassificationExperiment
from SecuML.Experiment.ClusteringExperiment import ClusteringExperiment
from SecuML.Tools import matrix_tools

class AlertsMonitoring(object):

    def __init__(self, datasets, predictions_monitoring, supervised_exp):
        self.datasets               = datasets
        self.predictions_monitoring = predictions_monitoring
        self.supervised_exp         = supervised_exp
        self.alerts_conf = supervised_exp.classification_conf.test_conf.alerts_conf

    def generateAlerts(self, directory):
        alerts_ids = self.generateAlertsCsvFile(directory)
        self.alertsGrouping(alerts_ids, directory)

    def generateAlertsCsvFile(self, directory):
        detection_threshold = self.alerts_conf.detection_threshold
        with open(directory + 'alerts.csv', 'w') as f:
            alerts = matrix_tools.extractRowsWithThresholds(
                    self.predictions_monitoring.predictions,
                    detection_threshold, None,
                    'predicted_proba')
            alerts = matrix_tools.sortDataFrame(alerts, 'predicted_proba', False, False)
            alerts.to_csv(f, index_label = 'instance_id')
        return list(alerts.index.values)

    def alertsGrouping(self, alerts_ids, directory):
        if len(alerts_ids) > 0:
            has_families = labels_tools.datasetHasFamilies(self.supervised_exp.cursor,
                    self.supervised_exp.project, self.supervised_exp.dataset,
                    self.supervised_exp.experiment_label_id)
            if has_families:
                self.alertsClassification(alerts_ids)
            else:
                self.alertsClustering(alerts_ids)
        else:
            self.grouping_exp_id = None
        with open(directory + 'grouping.json', 'w') as f:
            grouping = {'grouping_exp_id': self.grouping_exp_id}
            json.dump(grouping, f, indent = 2)

    def alertsClustering(self, alerts_ids):
        self.checkNumClustersValidity(alerts_ids)
        clustering_exp = self.createClusteringExperiment()
        self.grouping_exp_id = clustering_exp.experiment_id
        clustering_conf = self.alerts_conf.clustering_conf
        clustering_analysis = clustering_conf.algo(self.datasets.test_instances.getInstancesFromIds(alerts_ids),
                                                   clustering_exp)
        clustering_analysis.run(quick = True, drop_annotated_instances = False)

    def checkNumClustersValidity(self, alerts_ids):
        num_alerts = len(alerts_ids)
        num_clusters = self.alerts_conf.clustering_conf.num_clusters
        if num_alerts < num_clusters:
            message  = 'Cannot build ' + str(num_clusters) + ' clusters '
            message += 'from ' + str(num_alerts) + ' alerts. '
            message += 'num_clusters should be smaller than num_alerts.\n'
            num_clusters = min(num_alerts, 4)
            self.alerts_conf.clustering_conf.num_clusters = num_clusters
            message += 'The number of clusters is set to ' + str(num_clusters) + '.'
            warnings.warn(message)

    def createClusteringExperiment(self, num_clusters = None):
        exp = self.supervised_exp
        test_exp = exp.classification_conf.test_conf.test_exp
        if test_exp is None:
            test_exp = exp
        name = exp.experiment_name + '_alertsClustering'
        if num_clusters is None:
            clustering_conf = self.alerts_conf.clustering_conf
        else:
            clustering_conf = ClusteringConfiguration(num_clusters)
        clustering_experiment = ClusteringExperiment(
                exp.project, test_exp.dataset, exp.db, exp.cursor,
                clustering_conf,
                experiment_name = name,
                experiment_label = test_exp.experiment_label,
                parent = test_exp.experiment_id)
        clustering_experiment.setFeaturesFilenames(test_exp.features_filenames)
        clustering_experiment.createExperiment()
        clustering_experiment.export()
        return clustering_experiment

    def alertsClassification(self, alerts_ids):
        multiclass_model = self.buildMulticlassClassifier(alerts_ids)
        num_families = len(self.datasets.train_instances.getFamiliesValues(label = 'malicious'))
        clustering_experiment = self.createClusteringExperiment(num_clusters = num_families)
        self.grouping_exp_id = clustering_experiment.experiment_id
        all_families = list(multiclass_model.class_labels)
        predicted_families = multiclass_model.testing_monitoring.getPredictedLabels()
        predicted_families = [all_families.index(x) for x in predicted_families]
        clustering = Clustering(clustering_experiment,
                multiclass_model.datasets.test_instances,
                predicted_families)
        clustering.generateClustering(None, None, cluster_labels = all_families)

    def buildMulticlassClassifier(self, alerts_ids):
        multiclass_exp = self.createMulticlassExperiment()
        multiclass_datasets = ClassifierDatasets(multiclass_exp, multiclass_exp.classification_conf)
        malicious_ids = self.datasets.train_instances.getMaliciousIds()
        multiclass_datasets.train_instances = self.datasets.train_instances.getInstancesFromIds(malicious_ids)
        multiclass_datasets.test_instances  = self.datasets.test_instances.getInstancesFromIds(alerts_ids)
        multiclass_datasets.setSampleWeights()
        multiclass_model = multiclass_exp.classification_conf.model_class(multiclass_exp, multiclass_datasets,
                                                                          cv_monitoring = False)
        multiclass_model.run()
        return multiclass_model

    def createMulticlassExperiment(self):
        exp  = self.supervised_exp
        name = exp.experiment_name + '_alertsMulticlassClassifier'
        multiclass_exp = ClassificationExperiment(exp.project, exp.dataset, exp.db, exp.cursor,
                experiment_name = name,
                experiment_label = exp.experiment_label,
                parent = exp.experiment_id)
        multiclass_exp.setFeaturesFilenames(exp.features_filenames)
        params = {}
        params['num_folds'] = exp.classification_conf.num_folds
        params['sample_weight'] = False
        params['families_supervision'] = True
        params['optim_algo'] = 'liblinear'
        params['alerts_conf'] = None
        test_conf = TestConfiguration()
        test_conf.setUnlabeled(labels_annotations = 'annotations')
        params['test_conf'] = test_conf
        conf = ClassifierConfFactory.getFactory().fromParam(
                'LogisticRegression', params)
        multiclass_exp.setClassifierConf(conf)
        multiclass_exp.createExperiment()
        multiclass_exp.export()
        return multiclass_exp
