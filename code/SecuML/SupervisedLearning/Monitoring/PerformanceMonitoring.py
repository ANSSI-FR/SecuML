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
from Errors import Errors
from PerfIndicators import PerfIndicators
from ROC import ROC

class PerformanceMonitoring(object):

    def __init__(self, num_folds = 1):
        self.confusion_matrix    = ConfusionMatrix()
        self.perf_indicators     = PerfIndicators(num_folds)
        self.roc                 = ROC(num_folds)
        self.errors              = Errors()

    def addFold(self, fold, true_labels, instances_ids, predicted_proba):
        predicted_labels = self.perf_indicators.addFold(fold, true_labels, 
                predicted_proba)
        self.confusion_matrix.addFold(true_labels, predicted_labels)
        self.roc.addFold(fold, true_labels, predicted_proba)
        self.errors.addFold(true_labels, instances_ids, predicted_proba)
        return predicted_labels

    def finalComputations(self):
        self.perf_indicators.finalComputations()

    def display(self, directory):
        with open(directory + 'confusion_matrix.json', 'w') as f:
            self.confusion_matrix.toJson(f)
        with open(directory + 'perf_indicators.json', 'w') as f:
            self.perf_indicators.toJson(f)
        self.roc.display(directory)
        with open(directory + 'errors.json', 'w') as f:
            self.errors.toJson(f)
