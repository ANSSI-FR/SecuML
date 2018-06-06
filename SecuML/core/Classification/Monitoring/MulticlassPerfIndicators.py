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

import json
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

from SecuML.core.Clustering.Evaluation.PerformanceIndicators import PerformanceIndicators
from SecuML.core.Tools import floats_tools


class MulticlassPerfIndicators(object):

    def __init__(self, num_folds):
        self.num_folds = num_folds
        self.accuracy = [0] * num_folds
        self.f1_micro = [0] * num_folds
        self.f1_macro = [0] * num_folds
        self.clustering_perf = PerformanceIndicators()
        self.ground_truth = []
        self.predictions = []

    def setFscores(self, fold_id, predictions):
        diff = set(predictions.ground_truth) - set(predictions.predictions)
        if predictions.numInstances() > 0 and len(diff) == 0:
            self.f1_micro[fold_id] = f1_score(predictions.ground_truth,
                                              predictions.predictions,
                                              average='micro')
            self.f1_macro[fold_id] = f1_score(predictions.ground_truth,
                                              predictions.predictions,
                                              average='macro')
        else:
            self.f1_micro[fold_id] = 0
            self.f1_macro[fold_id] = 0

    def setAccuracy(self, fold_id, predictions):
        if predictions.numInstances() == 0:
            self.accuracy[fold_id] = 0
        else:
            self.accuracy[fold_id] = accuracy_score(predictions.ground_truth,
                                                    predictions.predictions)

    def addFold(self, fold_id, predictions):
        self.setFscores(fold_id, predictions)
        self.setAccuracy(fold_id, predictions)
        self.updateGroundTruthPredictions(predictions)

    def updateGroundTruthPredictions(self, predictions):
        self.ground_truth += predictions.ground_truth
        self.predictions += predictions.predictions

    def getAccuracy(self):
        return self.accuracy_mean

    def finalComputations(self):
        self.accuracy_mean = np.mean(self.accuracy)
        self.accuracy_std = np.std(self.accuracy)
        self.f1_micro_mean = np.mean(self.f1_micro)
        self.f1_micro_std = np.std(self.f1_micro)
        self.f1_macro_mean = np.mean(self.f1_macro)
        self.f1_macro_std = np.std(self.f1_macro)
        self.clustering_perf.generateEvaluation(
            self.ground_truth, self.predictions)

    def toJson(self, f):
        perf = {}
        perf['accuracy'] = {'mean': floats_tools.toPercentage(self.accuracy_mean),
                            'std': floats_tools.trunc(self.accuracy_std)}
        perf['f1_micro'] = {'mean': floats_tools.toPercentage(self.f1_micro_mean),
                            'std': floats_tools.trunc(self.f1_micro_std)}
        perf['f1_macro'] = {'mean': floats_tools.toPercentage(self.f1_macro_mean),
                            'std': floats_tools.trunc(self.f1_macro_std)}
        perf['clustering_perf'] = self.clustering_perf.toJson()
        json.dump(perf, f, indent=2)

    def getCsvHeader(self):
        return ['accuracy', 'f1-micro', 'f1-macro']

    def getCsvLine(self):
        v = []
        v.append(self.accuracy_mean)
        v.append(self.f1_micro_mean)
        v.append(self.f1_macro_mean)
        return v
