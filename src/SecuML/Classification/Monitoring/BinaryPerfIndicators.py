## SecuML
## Copyright (C) 2016-2017  ANSSI
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
import math
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc, precision_recall_fscore_support, accuracy_score

from SecuML.Tools import floats_tools

# The thresholds are considered only for probabilist models

class BinaryPerfIndicators(object):

    def __init__(self, num_folds, probabilist_model, auc = True):
        self.probabilist_model = probabilist_model
        self.auc               = auc
        self.num_folds         = num_folds
        if self.auc:
            self.fold_auc          = [0] * num_folds
        if self.probabilist_model:
            self.thresholds = range(101)
            self.fold_perf = [np.zeros((num_folds, 4)) for x in self.thresholds]
        else:
            self.fold_perf = np.zeros((num_folds, 5))

    def addFold(self, fold_id, true_labels, predicted_proba, predicted_scores, predicted_labels):
        if self.auc:
            self.addAuc(fold_id, true_labels, predicted_proba, predicted_scores)
        if self.probabilist_model:
            self.addProbabilistFold(fold_id, true_labels, predicted_proba, threshold = None)
        else:
            self.addNonProbabilistFold(fold_id, true_labels, predicted_labels)

    def addAuc(self, fold_id, true_labels, predicted_proba, predicted_scores):
        scores = predicted_proba if self.probabilist_model else predicted_scores
        if len(true_labels) == 0:
            roc_auc = 0
        else:
            fpr, tpr, thresholds = roc_curve(true_labels, scores)
            roc_auc = auc(fpr, tpr)
            if math.isnan(roc_auc):
                roc_auc = 0
        self.fold_auc[fold_id] = roc_auc

    def addProbabilistFold(self, fold_id, true_labels, predicted_proba, threshold = None):
        if threshold is None:
            for threshold in self.thresholds:
                self.addProbabilistFold(fold_id, true_labels, predicted_proba, threshold = threshold)
        else:
            predicted_labels = np.array(predicted_proba) > threshold / 100
            precision, recall, f_score, _ = precision_recall_fscore_support(true_labels, predicted_labels,
                                                                            average = 'binary')
            if len(predicted_labels) == 0:
                fp = 0
                tn = 0
            else:
                conf_matrix = confusion_matrix(true_labels, predicted_labels, [True, False])
                fp = conf_matrix[1][0]
                tn = conf_matrix[1][1]
            fp_tn = fp + tn
            if fp_tn == 0:
                false_alarm_rate = 0
            else:
                false_alarm_rate = fp / (fp + tn)
            self.fold_perf[threshold][fold_id, :] = [precision, recall, false_alarm_rate, f_score]

    def addNonProbabilistFold(self, fold_id, true_labels, predicted_labels):
        precision, recall, f_score, _ = precision_recall_fscore_support(true_labels, predicted_labels,
                                                                        average = 'binary')
        accuracy = accuracy_score(true_labels, predicted_labels)
        if len(predicted_labels) == 0:
                fp = 0
                tn = 0
        else:
            conf_matrix = confusion_matrix(true_labels, predicted_labels, [True, False])
            fp = conf_matrix[1][0]
            tn = conf_matrix[1][1]
        fp_tn = fp + tn
        if fp_tn == 0:
            false_alarm_rate = 0
        else:
            false_alarm_rate = fp / (fp + tn)
        self.fold_perf[fold_id, :] = [precision, recall, false_alarm_rate, f_score, accuracy]

    def finalComputations(self):
        if self.auc:
            self.auc_mean = np.mean(self.fold_auc)
            self.auc_std  = np.std(self.fold_auc)
        if self.probabilist_model:
            self.fold_perf = [pd.DataFrame(self.fold_perf[x],
                    index = ['f_' + str(x) for x in range(self.num_folds)],
                    columns = ['precision', 'recall', 'false_positive', 'f-score'])
                    for x in self.thresholds]
            indicators = self.fold_perf[0].columns
            columns    = ['mean', 'std']
            self.perf_threshold_summary = [pd.DataFrame(
                    np.zeros((len(indicators), len(columns))),
                    columns = columns,
                    index = indicators)
                    for x in self.thresholds]
            for threshold in self.thresholds:
                if self.num_folds > 1:
                    mean_perf = self.fold_perf[threshold].mean(axis = 0)
                    std_perf = self.fold_perf[threshold].std(axis = 0)
                else:
                    mean_perf = self.fold_perf[threshold].iloc[0, ]
                    std_perf = [0] * len(indicators)
                self.perf_threshold_summary[threshold]['mean'] = mean_perf
                self.perf_threshold_summary[threshold]['std']  = std_perf
        else:
            self.fold_perf = pd.DataFrame(self.fold_perf,
                    index = ['f_' + str(x) for x in range(self.num_folds)],
                    columns = ['precision', 'recall', 'false_positive', 'f-score', 'accuracy'])
            indicators = self.fold_perf.columns
            columns    = ['mean', 'std']
            self.perf_threshold_summary = pd.DataFrame(
                    np.zeros((len(indicators), len(columns))),
                    columns = columns,
                    index = indicators)
            if self.num_folds > 1:
                mean_perf = self.fold_perf.mean(axis = 0)
                std_perf = self.fold_perf.std(axis = 0)
            else:
                mean_perf = self.fold_perf.iloc[0, ]
                std_perf = [0] * len(indicators)
            self.perf_threshold_summary['mean'] = mean_perf
            self.perf_threshold_summary['std']  = std_perf

    def getPerfEstimator(self, estimator, threshold):
        if self.probabilist_model:
            return self.perf_threshold_summary[threshold].loc[estimator, 'mean']
        else:
            return self.perf_threshold_summary.loc[estimator, 'mean']

    def getFalseAlarmRate(self, threshold = 50):
        return self.getPerfEstimator('false_positive', threshold)

    def getDetectionRate(self, threshold = 50):
        return self.getPerfEstimator('recall', threshold)

    def getPrecision(self, threshold = 50):
        return self.getPerfEstimator('precision', threshold)

    def getRecall(self, threshold = 50):
        return self.getPerfEstimator('recall', threshold)

    def getFscore(self, threshold = 50):
        return self.getPerfEstimator('f-score', threshold)

    def getAccuracy(self, threshold = 50):
        return self.getPerfEstimator('accuracy', threshold)

    def getAuc(self):
        return self.auc_mean

    def getCsvHeader(self):
        return ['auc', 'fscore', 'precision', 'recall']

    def getCsvLine(self):
        v = []
        v.append(self.getAuc())
        v.append(self.getFscore())
        v.append(self.getPrecision())
        v.append(self.getRecall())
        return v

    def toJson(self, f):
        perf = {}
        if self.auc:
            perf['auc'] = {'mean': str(int(self.auc_mean*10000)/100) + '%',
                    'std': int(self.auc_std*10000)/10000}
        if self.probabilist_model:
            perf['thresholds'] = [{} for x in self.thresholds]
            for t in self.thresholds:
                for v in self.perf_threshold_summary[t].index:
                    perf['thresholds'][t][v] = {}
                    perf['thresholds'][t][v]['mean'] = str(int(self.perf_threshold_summary[t].loc[v, 'mean']*10000)/100)
                    perf['thresholds'][t][v]['mean'] += '%'
                    perf['thresholds'][t][v]['std']  = int(self.perf_threshold_summary[t].loc[v, 'std']*10000)/10000
        else:
            for v in self.perf_threshold_summary.index:
                perf[v] = {}
                perf[v]['mean'] = floats_tools.toPercentage(self.perf_threshold_summary.loc[v, 'mean'])
                perf[v]['std']  = floats_tools.trunc(self.perf_threshold_summary.loc[v, 'std'])
        json.dump(perf, f, indent = 2)
