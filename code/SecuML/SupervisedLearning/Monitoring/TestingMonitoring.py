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

from SecuML.Tools import dir_tools

from FamiliesMonitoring import FamiliesMonitoring
from PerformanceMonitoring import PerformanceMonitoring
from PredictionsMonitoring import PredictionsMonitoring

class TestingMonitoring(object):

    ## monitoring_type in ['test', 'validation']
    def __init__(self, testing_labels, testing_sublabels, 
            monitoring_type = 'test'):
        self.monitoring_type = monitoring_type
        self.predictions_monitoring = PredictionsMonitoring()
        ## When the true labels are known
        self.has_true_labels = all(l is not None for l in testing_labels)
        self.testing_labels = testing_labels
        self.testing_sublabels = testing_sublabels
        if self.has_true_labels:
            self.performance_monitoring = PerformanceMonitoring()
            self.families_monitoring = FamiliesMonitoring()
    
    def addPredictions(self, predicted_proba, predicted_scores, instances_ids):
        if self.has_true_labels:
            predicted_labels = self.performance_monitoring.addFold(
                    0, self.testing_labels,
                    instances_ids, predicted_proba)
            self.families_monitoring.addFold(predicted_proba, 
                    self.testing_labels, self.testing_sublabels)
        else:
            predicted_labels = [x > 0.5 for x in predicted_proba]
        self.predictions_monitoring.addFold(instances_ids,
                predicted_proba, predicted_scores,
                predicted_labels, self.testing_labels)

    def finalComputations(self):
        self.predictions_monitoring.finalComputations()
        if self.has_true_labels:
            self.performance_monitoring.finalComputations()
            self.families_monitoring.finalComputations()

    def display(self, directory):
        testing_dir = directory + self.monitoring_type + '/'
        dir_tools.createDirectory(testing_dir)
        self.finalComputations()
        self.predictions_monitoring.display(testing_dir)
        if self.has_true_labels:
            self.performance_monitoring.display(testing_dir)
            families_dir = testing_dir + 'families/'
            dir_tools.createDirectory(families_dir)
            self.families_monitoring.display(families_dir)
