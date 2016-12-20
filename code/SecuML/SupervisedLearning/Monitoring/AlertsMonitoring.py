## SecuML
## Copyright (C) 2016  ANSSI
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

import pandas as pd

from SecuML.Data.Instances import Instances
from SecuML.Experiment.ClusteringExperiment import ClusteringExperiment
from SecuML.Tools import matrix_tools

class AlertsMonitoring(object):

    def __init__(self, datasets, predictions_monitoring, supervised_exp):
        self.datasets               = datasets
        self.predictions_monitoring = predictions_monitoring
        self.supervised_exp         = supervised_exp
        self.alerts_conf = supervised_exp.supervised_learning_conf.test_conf.alerts_conf

    def generateAlerts(self, directory):
        alerts_ids = self.generateAlertsCsvFile(directory)
        self.alertsClustering(alerts_ids)

    def generateAlertsCsvFile(self, directory):
        detection_threshold = self.alerts_conf.detection_threshold
        with open(directory + 'alerts.csv', 'w') as f:
            alerts = matrix_tools.extractRowsWithThresholds(
                    self.predictions_monitoring.predictions,
                    detection_threshold, None,
                    'predicted_proba')
            if pd.__version__ in ['0.13.0', '0.14.1']:
                alerts = alerts.sort(['predicted_proba'],
                        ascending = [False], inplace = False)
            else:
                alerts = alerts.sort_values(['predicted_proba'],
                        ascending = [False], inplace = False)
            alerts.to_csv(f, index_label = 'instance_id')
        return list(alerts.index.values)

    def alertsClustering(self, alerts_ids):
        annotated_instances = self.datasets.train_instances.getInstancesFromIds(
                self.datasets.train_instances.getMaliciousIds())
        num_malicious_families = len(annotated_instances.getSublabelsValues(label = 'malicious'))
        clustering_exp = self.createClusteringExperiment(num_malicious_families) 
        alerts_instances = self.datasets.test_instances.getInstancesFromIds(alerts_ids)
        instances = Instances()
        instances.union(alerts_instances, annotated_instances)
        clustering_conf = self.alerts_conf.clustering_conf
        clustering_analysis = clustering_conf.algo(instances, clustering_exp)
        clustering_analysis.run(quick = True, drop_annotated_instances = True)

    def createClusteringExperiment(self, num_malicious_families):
        exp = self.supervised_exp
        test_exp = exp.supervised_learning_conf.test_conf.test_exp
        if test_exp is None:
            test_exp = exp
        name = exp.experiment_name + '_alertsClustering'
        if num_malicious_families > 2:
            self.alerts_conf.clustering_conf.num_clusters = num_malicious_families
        clustering_conf = self.alerts_conf.clustering_conf
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

    @staticmethod
    def getAlertsClusteringExperimentId(cursor, experiment_id):
        query  = 'SELECT id FROM Experiments '
        query += 'WHERE kind = "Clustering" '
        query += 'AND parent = ' + str(experiment_id) + ';'
        cursor.execute(query)
        row = cursor.fetchone()
        clustering_exp_id = None
        if row is not None:
            clustering_exp_id = row[0]
        return clustering_exp_id
