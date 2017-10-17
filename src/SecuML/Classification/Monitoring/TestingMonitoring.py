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
    def __init__(self, conf, testing_labels, testing_families, monitoring_type = 'test'):
        self.conf                   = conf
        self.monitoring_type        = monitoring_type
        self.predictions_monitoring = PredictionsMonitoring(self.conf)

        ## When the true labels are known
        self.has_true_labels = all(l is not None for l in testing_labels)
        self.testing_labels = testing_labels
        self.testing_families = testing_families
        self.families_monitoring = None
        if self.has_true_labels:
            self.performance_monitoring = PerformanceMonitoring(1, self.conf)
            if not self.conf.families_supervision:
                if self.conf.getModelClassName() != 'Sssvdd':
                    self.families_monitoring = FamiliesMonitoring()

    def addPredictions(self, predictions, instances_ids):
        if self.has_true_labels:
            true = self.testing_labels
            if self.conf.families_supervision:
                true = self.testing_families
            self.performance_monitoring.addFold(0, true, instances_ids, predictions)
            if self.families_monitoring is not None:
                self.families_monitoring.addFold(predictions.predicted_proba,
                        self.testing_labels, self.testing_families)
        self.predictions_monitoring.addFold(instances_ids, predictions,
                                            self.testing_labels)

    def finalComputations(self):
        self.predictions_monitoring.finalComputations()
        if self.has_true_labels:
            self.performance_monitoring.finalComputations()
            if self.families_monitoring is not None:
                self.families_monitoring.finalComputations()

    def display(self, directory):
        testing_dir = directory + self.monitoring_type + '/'
        dir_tools.createDirectory(testing_dir)
        self.finalComputations()
        self.predictions_monitoring.display(testing_dir)
        if self.has_true_labels:
            self.performance_monitoring.display(testing_dir)
            if self.families_monitoring is not None:
                families_dir = testing_dir + 'families/'
                dir_tools.createDirectory(families_dir)
                self.families_monitoring.display(families_dir)

    def getPredictedLabels(self):
        return self.predictions_monitoring.getPredictedLabels()

    def getAllPredictedProba(self):
        return self.predictions_monitoring.getAllPredictedProba()
