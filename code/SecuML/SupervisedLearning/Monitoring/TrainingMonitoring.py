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
    def __init__(self, conf, features,
            monitoring_type = 'train'):
        num_folds = 1
        if monitoring_type == 'cv':
            num_folds = conf.num_folds
        self.monitoring_type = monitoring_type
        self.performance_monitoring = PerformanceMonitoring(num_folds)
        self.predictions_monitoring = PredictionsMonitoring()
        self.coefficients           = Coefficients(num_folds, features)
        self.families_monitoring    = FamiliesMonitoring()

    def addFold(self, fold, true_labels, true_sublabels, instances_ids, predicted_proba, predicted_scores, coef):
        predicted_labels = self.performance_monitoring.addFold(fold,
                true_labels, instances_ids, predicted_proba)
        self.predictions_monitoring.addFold(instances_ids,
                predicted_proba, predicted_scores, predicted_labels, true_labels)
        self.coefficients.addFold(fold, coef)
        self.families_monitoring.addFold(predicted_proba, true_labels, true_sublabels)

    def finalComputations(self):
        self.performance_monitoring.finalComputations()
        self.predictions_monitoring.finalComputations()
        self.coefficients.finalComputations()
        self.families_monitoring.finalComputations()

    def display(self, directory):
        training_dir = directory + self.monitoring_type + '/'
        dir_tools.createDirectory(training_dir)
        self.finalComputations()
        self.performance_monitoring.display(training_dir)
        self.predictions_monitoring.display(training_dir)
        self.coefficients.display(training_dir)
        families_dir = training_dir + 'families/'
        dir_tools.createDirectory(families_dir)
        self.families_monitoring.display(families_dir)
