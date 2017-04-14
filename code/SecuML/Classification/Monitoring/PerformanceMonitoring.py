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

from ConfusionMatrix import ConfusionMatrix
from BinaryErrors import BinaryErrors
from BinaryPerfIndicators import BinaryPerfIndicators
from MulticlassErrors import MulticlassErrors
from MulticlassPerfIndicators import MulticlassPerfIndicators
from ROC import ROC

class PerformanceMonitoring(object):

    def __init__(self, num_folds, conf):
        self.conf = conf
        if self.conf.families_supervision:
            self.perf_indicators = MulticlassPerfIndicators(num_folds)
            self.errors          = MulticlassErrors()
        else:
            self.perf_indicators  = BinaryPerfIndicators(num_folds, conf.probabilistModel())
            self.errors           = BinaryErrors(conf)
            self.confusion_matrix = ConfusionMatrix()
            self.roc              = ROC(num_folds, conf)

    def addFold(self, fold, true_labels, instances_ids, predicted_proba, predicted_scores, predicted_labels):
        if self.conf.families_supervision:
            self.perf_indicators.addFold(fold, true_labels, predicted_labels)
            self.errors.addFold(true_labels, instances_ids, predicted_labels)
        else:
            self.perf_indicators.addFold(fold, true_labels, predicted_proba, predicted_scores, predicted_labels)
            self.errors.addFold(true_labels, instances_ids, predicted_labels, predicted_proba, predicted_scores)
            self.confusion_matrix.addFold(true_labels, predicted_labels)
            self.roc.addFold(fold, true_labels, predicted_proba, predicted_scores)

    def finalComputations(self):
        self.perf_indicators.finalComputations()

    def display(self, directory):
        with open(directory + 'perf_indicators.json', 'w') as f:
            self.perf_indicators.toJson(f)
        with open(directory + 'errors.json', 'w') as f:
            self.errors.toJson(f)
        if not self.conf.families_supervision:
            with open(directory + 'confusion_matrix.json', 'w') as f:
                self.confusion_matrix.toJson(f)
            self.roc.display(directory)
