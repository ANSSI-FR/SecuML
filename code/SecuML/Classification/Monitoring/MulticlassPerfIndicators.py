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

from __future__ import division

import json
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

from SecuML.Clustering.Evaluation.PerformanceIndicators import PerformanceIndicators

class MulticlassPerfIndicators(object):

    def __init__(self, num_folds):
        self.num_folds = num_folds
        self.accuracy  = [0] * num_folds
        self.f1_micro  = [0] * num_folds
        self.f1_macro  = [0] * num_folds
        self.clustering_perf  = PerformanceIndicators()
        self.true_labels      = []
        self.predicted_labels = []

    def addFold(self, fold_id, true_labels, predicted_labels):
        self.f1_micro[fold_id] = f1_score(true_labels, predicted_labels, average = 'micro')
        self.f1_macro[fold_id] = f1_score(true_labels, predicted_labels, average = 'macro')
        self.accuracy[fold_id] = accuracy_score(true_labels, predicted_labels)
        self.true_labels      += true_labels
        self.predicted_labels += list(predicted_labels)

    def getAccuracy(self):
        return self.accuracy_mean

    def finalComputations(self):
        self.accuracy_mean = np.mean(self.accuracy)
        self.accuracy_std  = np.std(self.accuracy)
        self.f1_micro_mean = np.mean(self.f1_micro)
        self.f1_micro_std  = np.std(self.f1_micro)
        self.f1_macro_mean = np.mean(self.f1_macro)
        self.f1_macro_std  = np.std(self.f1_macro)
        self.clustering_perf.generateEvaluation(self.true_labels, self.predicted_labels)

    def toJson(self, f):
        perf = {}
        perf['accuracy'] = {'mean': str(int(self.accuracy_mean*10000)/100) + '%',
                'std': int(self.accuracy_std*10000)/10000}
        perf['f1_micro'] = {'mean': str(int(self.f1_micro_mean*10000)/100) + '%',
                'std': int(self.f1_micro_std*10000)/10000}
        perf['f1_macro'] = {'mean': str(int(self.f1_macro_mean*10000)/100) + '%',
                'std': int(self.f1_macro_std*10000)/10000}
        perf['clustering_perf'] = self.clustering_perf.toJson()
        json.dump(perf, f, indent = 2)

    def getCsvHeader(self):
        return ['accuracy', 'f1-micro', 'f1-macro']

    def getCsvLine(self):
        v = []
        v.append(self.accuracy_mean)
        v.append(self.f1_micro_mean)
        v.append(self.f1_macro_mean)
        return v
