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

from Coefficients import Coefficients
from FamiliesMonitoring import FamiliesMonitoring
from PerformanceMonitoring import PerformanceMonitoring
from PredictionsMonitoring import PredictionsMonitoring

class TrainingMonitoring(object):

    ## monitoring_type in ['train', 'cv']
    def __init__(self, conf, features, monitoring_type = 'train'):
        self.conf = conf
        self.monitoring_type = monitoring_type
        self.setNumFolds()
        self.performance_monitoring = PerformanceMonitoring(1, self.conf)

        self.families_monitoring = None
        if not self.conf.families_supervision:
            self.predictions_monitoring = PredictionsMonitoring(self.conf)
            self.coefficients           = Coefficients(self.num_folds, features)
            if self.conf.getModelClassName() != 'Sssvdd' and self.conf.getModelClassName() != 'SssvddOriginal':
                self.families_monitoring    = FamiliesMonitoring()

    def addFold(self, fold, true_labels, true_families, instances_ids, predicted_proba_all,
            predicted_proba, predicted_scores, predicted_labels, coef):
        true = true_labels
        if self.conf.families_supervision:
            true = true_families
        self.performance_monitoring.addFold(fold, true, instances_ids, predicted_proba,
                                                               predicted_scores, predicted_labels)
        if not self.conf.families_supervision:
            self.predictions_monitoring.addFold(instances_ids,
                    predicted_proba_all, predicted_proba, predicted_scores, predicted_labels, true_labels)
            self.coefficients.addFold(fold, coef)
            if self.families_monitoring is not None:
                self.families_monitoring.addFold(predicted_proba, true_labels, true_families)

    def finalComputations(self):
        self.performance_monitoring.finalComputations()
        if not self.conf.families_supervision:
            self.predictions_monitoring.finalComputations()
            self.coefficients.finalComputations()
            if self.families_monitoring is not None:
                self.families_monitoring.finalComputations()

    def display(self, directory):
        training_dir = directory + self.monitoring_type + '/'
        dir_tools.createDirectory(training_dir)
        self.finalComputations()
        self.performance_monitoring.display(training_dir)
        if not self.conf.families_supervision:
            self.predictions_monitoring.display(training_dir)
            self.coefficients.display(training_dir)
            if self.families_monitoring is not None:
                families_dir = training_dir + 'families/'
                dir_tools.createDirectory(families_dir)
                self.families_monitoring.display(families_dir)

    def setNumFolds(self):
        self.num_folds = 1
        if self.monitoring_type == 'cv':
            self.num_folds = self.conf.num_folds
