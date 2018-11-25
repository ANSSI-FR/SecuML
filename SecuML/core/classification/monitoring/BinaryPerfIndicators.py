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
import math
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc, accuracy_score, f1_score, \
    precision_score, recall_score

from SecuML.core.tools import floats_tools

# The thresholds are considered only for probabilist models


class BinaryPerfIndicators(object):

    def __init__(self, num_folds, probabilist_model, auc=True):
        self.probabilist_model = probabilist_model
        self.auc = auc
        self.num_folds = num_folds
        if self.auc:
            self.fold_auc = [0] * num_folds
        if self.probabilist_model:
            self.thresholds = list(range(101))
            self.columns = ['precision', 'recall', 'far', 'false_positive',
                            'f-score']
            self.fold_perf = [np.zeros((num_folds, len(self.columns)))
                              for x in self.thresholds]
        else:
            self.columns = ['precision', 'recall', 'far',
                            'false_positive', 'f-score', 'accuracy']
            self.fold_perf = np.zeros((num_folds, len(self.columns)))

    def addFold(self, fold_id, predictions):
        if self.auc:
            self.addAuc(fold_id, predictions)
        if self.probabilist_model:
            self.addProbabilistFold(fold_id, predictions, threshold=None)
        else:
            self.addNonProbabilistFold(fold_id, predictions)

    def addAuc(self, fold_id, predictions):
        if self.probabilist_model:
            scores = predictions.predicted_proba
        else:
            scores = predictions.predicted_scores
        if (predictions.numInstances() == 0
                or sum(predictions.ground_truth) == 0):
            roc_auc = 0
        else:
            fpr, tpr, thresholds = roc_curve(predictions.ground_truth, scores)
            roc_auc = auc(fpr, tpr)
            if math.isnan(roc_auc):
                roc_auc = 0
        self.fold_auc[fold_id] = roc_auc

    def computePrecisionRecallFscore(self, ground_truth_labels,
                                     predicted_labels):
        if len(ground_truth_labels) == 0:
            return 0, 0, 0
        # Check the presence of all the ground_truth_labels in predicted_labels
        diff = set(ground_truth_labels) - set(predicted_labels)
        if len(diff) != 0:
            precision = 0
            f_score = 0
        else:
            precision = precision_score(ground_truth_labels,
                                        predicted_labels,
                                        average='binary')
            f_score = f1_score(ground_truth_labels,
                               predicted_labels,
                               average='binary')
        # Check the presence of positive examples in ground_truth_labels
        if sum(ground_truth_labels) > 0:
            recall = recall_score(ground_truth_labels,
                                  predicted_labels,
                                  average='binary')
        else:
            recall = 0
        return precision, recall, f_score

    def computeFalsePositiveRate(self, ground_truth_labels, predicted_labels):
        if len(predicted_labels) == 0:
            fp = 0
            tn = 0
        else:
            conf_matrix = confusion_matrix(ground_truth_labels,
                                           predicted_labels,
                                           [True, False])
            fp = conf_matrix[1][0]
            tn = conf_matrix[1][1]
        fp_tn = fp + tn
        if fp_tn == 0:
            false_positive_rate = 0
        else:
            false_positive_rate = fp / (fp + tn)
        return false_positive_rate

    def addProbabilistFold(self, fold_id, predictions, threshold=None):
        if threshold is None:
            for threshold in self.thresholds:
                self.addProbabilistFold(
                    fold_id, predictions, threshold=threshold)
        else:
            probas = predictions.predicted_proba
            predicted_labels = np.array(probas) > threshold / 100
            precision, recall, f_score = self.computePrecisionRecallFscore(
                                                    predictions.ground_truth,
                                                    predicted_labels)
            false_positive_rate = self.computeFalsePositiveRate(
                predictions.ground_truth, predicted_labels)
            self.fold_perf[threshold][fold_id, :] = [precision, recall,
                                                     1-precision,
                                                     false_positive_rate,
                                                     f_score]

    def addNonProbabilistFold(self, fold_id, predictions):
        precision, recall, f_score = self.computePrecisionRecallFscore(
                                                    predictions.ground_truth,
                                                    predictions.predictions)
        accuracy = accuracy_score(predictions.ground_truth,
                                  predictions.predictions)
        fpr = self.computeFalsePositiveRate(predictions.ground_truth,
                                            predictions.predictions)
        self.fold_perf[fold_id, :] = [precision, recall, 1-precision, fpr,
                                      f_score, accuracy]

    def finalComputations(self):
        if self.auc:
            self.auc_mean = np.mean(self.fold_auc)
            self.auc_std = np.std(self.fold_auc)
        if self.probabilist_model:
            self.fold_perf = [pd.DataFrame(self.fold_perf[x],
                                           index=['f_' + str(x) for x in range(
                                                            self.num_folds)],
                                           columns=self.columns)
                              for x in self.thresholds]
            indicators = self.fold_perf[0].columns
            columns = ['mean', 'std']
            n_indicators = len(indicators)
            n_columns = len(columns)
            self.perf_threshold_summary = [pd.DataFrame(np.zeros((n_indicators,
                                                                 n_columns)),
                                                        columns=columns,
                                                        index=indicators)
                                           for x in self.thresholds]
            for threshold in self.thresholds:
                if self.num_folds > 1:
                    mean_perf = self.fold_perf[threshold].mean(axis=0)
                    std_perf = self.fold_perf[threshold].std(axis=0)
                else:
                    mean_perf = self.fold_perf[threshold].iloc[0, ]
                    std_perf = [0] * len(indicators)
                self.perf_threshold_summary[threshold]['mean'] = mean_perf
                self.perf_threshold_summary[threshold]['std'] = std_perf
        else:
            self.fold_perf = pd.DataFrame(self.fold_perf,
                                          index=['f_' + str(x) for x in range(
                                                            self.num_folds)],
                                          columns=self.columns)
            indicators = self.fold_perf.columns
            columns = ['mean', 'std']
            n_indicators = len(indicators)
            n_columns = len(columns)
            self.perf_threshold_summary = pd.DataFrame(np.zeros((n_indicators,
                                                                n_columns)),
                                                       columns=columns,
                                                       index=indicators)
            if self.num_folds > 1:
                mean_perf = self.fold_perf.mean(axis=0)
                std_perf = self.fold_perf.std(axis=0)
            else:
                mean_perf = self.fold_perf.iloc[0, ]
                std_perf = [0] * len(indicators)
            self.perf_threshold_summary['mean'] = mean_perf
            self.perf_threshold_summary['std'] = std_perf

    def getPerfEstimator(self, estimator, threshold=50):
        if self.probabilist_model:
            return self.perf_threshold_summary[threshold].loc[estimator, 'mean']
        else:
            return self.perf_threshold_summary.loc[estimator, 'mean']

    def getAuc(self):
        return self.auc_mean

    def getCsvHeader(self):
        return ['auc', 'fscore', 'precision', 'recall']

    def getCsvLine(self):
        v = []
        v.append(self.getAuc())
        v.append(self.getPerfEstimator('f-score'))
        v.append(self.getPerfEstimator('precision'))
        v.append(self.getPerfEstimator('recall'))
        return v

    def to_json(self, f):
        perf = {}
        if self.auc:
            perf['auc'] = {'mean': floats_tools.toPercentage(self.auc_mean),
                           'std': floats_tools.trunc(self.auc_std)}
        if self.probabilist_model:
            perf['thresholds'] = [{} for x in self.thresholds]
            for t in self.thresholds:
                summary = self.perf_threshold_summary[t]
                for v in summary.index:
                    perf['thresholds'][t][v] = {}
                    perf['thresholds'][t][v]['mean'] = floats_tools.toPercentage(
                            summary.loc[v, 'mean'])
                    perf['thresholds'][t][v]['std'] = floats_tools.trunc(
                            summary.loc[v, 'std'])
        else:
            for v in self.perf_threshold_summary.index:
                perf[v] = {}
                perf[v]['mean'] = floats_tools.toPercentage(
                    self.perf_threshold_summary.loc[v, 'mean'])
                perf[v]['std'] = floats_tools.trunc(
                    self.perf_threshold_summary.loc[v, 'std'])
        json.dump(perf, f, indent=2)
