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
import math
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, confusion_matrix
from sklearn.metrics import roc_curve, auc, f1_score

class PerfIndicators(object):

    def __init__(self, num_folds):
        self.thresholds = range(101)
        self.fold_threshold_perf = [pd.DataFrame(np.zeros((num_folds, 4)),
                index = ['f_' + str(x) for x in range(num_folds)],
                columns = ['precision', 'recall', 'false_positive', 'f-score'])
                for x in self.thresholds]
        self.fold_auc = [0] * num_folds

    # Return the predicted labels for a detectino threshold of 50%
    def addFold(self, fold_id, true_labels, predicted_proba, threshold = None):
        if threshold is None:
            fpr, tpr, thresholds = roc_curve(true_labels, predicted_proba)
            roc_auc = auc(fpr, tpr)
            if math.isnan(roc_auc):
                roc_auc = 0
            self.fold_auc[fold_id] = roc_auc
            for threshold in self.thresholds:
                predicted_labels = self.addFold(fold_id, true_labels, predicted_proba, threshold = threshold)
                if threshold == 50:
                    predicted_labels_50 = predicted_labels
            return predicted_labels_50
        predicted_labels = [x > threshold / 100 for x in predicted_proba]
        precision = precision_score(true_labels, predicted_labels)
        recall = recall_score(true_labels, predicted_labels)
        f_score = f1_score(true_labels, predicted_labels)
        conf_matrix = confusion_matrix(true_labels, predicted_labels, 
                [True, False])
        fp = conf_matrix[1][0]
        tn = conf_matrix[1][1]
        fp_tn = fp + tn
        if fp_tn == 0:
            false_alarm_rate = 0
        else:
            false_alarm_rate = fp / (fp + tn)
        self.fold_threshold_perf[threshold].iloc[fold_id,:] = [precision, recall, 
                false_alarm_rate, f_score]
        return predicted_labels

    def finalComputations(self):
        self.auc_mean = np.mean(self.fold_auc)
        self.auc_std  = np.std(self.fold_auc)
        num_folds  = len(self.fold_threshold_perf[0].index)
        indicators = self.fold_threshold_perf[0].columns
        columns    = ['mean', 'std']
        self.perf_threshold_summary = [pd.DataFrame(
                np.zeros((len(indicators), len(columns))),
                columns = columns,
                index = indicators)
                for x in self.thresholds]
        for threshold in self.thresholds:
            if num_folds > 1:
                mean_perf = self.fold_threshold_perf[threshold].mean(axis = 0)
                std_perf = self.fold_threshold_perf[threshold].std(axis = 0)
            else:
                mean_perf = self.fold_threshold_perf[threshold].iloc[0,]
                std_perf = [0] * len(indicators)
            self.perf_threshold_summary[threshold].loc[:,'mean'] = mean_perf
            self.perf_threshold_summary[threshold].loc[:,'std']  = std_perf
   
    def getPerfEstimator(self, estimator, threshold):
        return self.perf_threshold_summary[threshold].loc[estimator, 'mean']

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

    def getAuc(self):
        return self.auc_mean

    def toJson(self, f):
        perf = {}
        perf['auc'] = {'mean': str(int(self.auc_mean*10000)/100) + '%', 
                'std': int(self.auc_std*10000)/10000}
        perf['thresholds'] = [{} for x in self.thresholds]
        for t in self.thresholds:
            for v in self.perf_threshold_summary[t].index:
                perf['thresholds'][t][v] = {}
                perf['thresholds'][t][v]['mean'] = str(int(self.perf_threshold_summary[t].loc[v, 'mean']*10000)/100) + '%'
                perf['thresholds'][t][v]['std']  = int(self.perf_threshold_summary[t].loc[v, 'std']*10000)/10000
        json.dump(perf, f, indent = 2)
