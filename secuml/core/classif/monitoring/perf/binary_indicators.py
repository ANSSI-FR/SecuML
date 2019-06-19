# SecuML
# Copyright (C) 2016-2019  ANSSI
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
from sklearn.metrics import roc_curve, auc, accuracy_score
from sklearn.metrics import precision_recall_fscore_support

from secuml.core.tools.float import to_percentage, trunc

# The thresholds are considered only for probabilist models


class BinaryIndicators(object):

    def __init__(self, num_folds, probabilist, with_scoring, auc=True):
        self.probabilist = probabilist
        self.with_scoring = with_scoring
        self.auc = auc
        self.num_folds = num_folds
        if self.auc:
            self.fold_auc = [0] * num_folds
        if self.probabilist:
            self.thresholds = list(range(101))
            self.columns = ['precision', 'recall', 'far', 'false_positive',
                            'f-score']
            self.fold_perf = [np.zeros((num_folds, len(self.columns)))
                              for x in self.thresholds]
        else:
            self.columns = ['precision', 'recall', 'far',
                            'false_positive', 'f-score', 'accuracy']
            self.fold_perf = np.zeros((num_folds, len(self.columns)))

    def add_fold(self, fold_id, predictions):
        if self.auc:
            self.add_auc(fold_id, predictions)
        if self.probabilist:
            self.add_proba_fold(fold_id, predictions, threshold=None)
        else:
            self.add_non_proba_fold(fold_id, predictions)

    def add_auc(self, fold_id, predictions):
        if self.probabilist:
            scores = predictions.probas
        else:
            scores = predictions.scores
        if not self.probabilist and not self.with_scoring:
            roc_auc = 0
        elif (predictions.num_instances() == 0
                or sum(predictions.ground_truth) == 0):
            roc_auc = 0
        else:
            fpr, tpr, thresholds = roc_curve(predictions.ground_truth, scores)
            roc_auc = auc(fpr, tpr)
            if math.isnan(roc_auc):
                roc_auc = 0
        self.fold_auc[fold_id] = roc_auc

    def compute_precision_recall_fscore(self, ground_truth, predictions):
        precision, recall, f_score, _ = precision_recall_fscore_support(
                                                ground_truth, predictions,
                                                average='binary',
                                                warn_for=())
        return precision, recall, f_score

    def compute_fpr(self, ground_truth, predictions):
        if len(predictions) == 0:
            fp = 0
            tn = 0
        else:
            conf_matrix = confusion_matrix(ground_truth, predictions,
                                           [True, False])
            fp = conf_matrix[1][0]
            tn = conf_matrix[1][1]
        fp_tn = fp + tn
        if fp_tn == 0:
            false_positive_rate = 0
        else:
            false_positive_rate = fp / (fp + tn)
        return false_positive_rate

    def add_proba_fold(self, fold_id, predictions, threshold=None):
        if threshold is None:
            for threshold in self.thresholds:
                self.add_proba_fold(
                    fold_id, predictions, threshold=threshold)
        else:
            probas = predictions.probas
            predicted_labels = np.array(probas) > threshold / 100
            precision, recall, f_score = self.compute_precision_recall_fscore(
                                                    predictions.ground_truth,
                                                    predicted_labels)
            false_positive_rate = self.compute_fpr(
                predictions.ground_truth, predicted_labels)
            self.fold_perf[threshold][fold_id, :] = [precision, recall,
                                                     1-precision,
                                                     false_positive_rate,
                                                     f_score]

    def add_non_proba_fold(self, fold_id, predictions):
        precision, recall, f_score = self.compute_precision_recall_fscore(
                                                    predictions.ground_truth,
                                                    predictions.values)
        accuracy = accuracy_score(predictions.ground_truth,
                                  predictions.values)
        fpr = self.compute_fpr(predictions.ground_truth, predictions.values)
        self.fold_perf[fold_id, :] = [precision, recall, 1-precision, fpr,
                                      f_score, accuracy]

    def final_computations(self):
        if self.auc:
            self.auc_mean = np.mean(self.fold_auc)
            self.auc_std = np.std(self.fold_auc)
        if self.probabilist:
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

    def get_perf_estimator(self, estimator, threshold=50):
        if self.probabilist:
            return self.perf_threshold_summary[threshold].loc[estimator,
                                                              'mean']
        else:
            return self.perf_threshold_summary.loc[estimator, 'mean']

    def get_auc(self):
        return self.auc_mean

    def get_csv_header(self):
        return ['auc', 'fscore', 'precision', 'recall']

    def get_csv_line(self):
        return [self.get_auc(),
                self.get_perf_estimator('f-score'),
                self.get_perf_estimator('precision'),
                self.get_perf_estimator('recall')]

    def to_json(self, f):
        perf = {}
        if self.auc:
            perf['auc'] = {'mean': to_percentage(self.auc_mean),
                           'std': trunc(self.auc_std)}
        if self.probabilist:
            perf['thresholds'] = [{} for x in self.thresholds]
            for t in self.thresholds:
                summary = self.perf_threshold_summary[t]
                for v in summary.index:
                    perf['thresholds'][t][v] = {}
                    perf['thresholds'][t][v]['mean'] = to_percentage(
                            summary.loc[v, 'mean'])
                    perf['thresholds'][t][v]['std'] = trunc(
                            summary.loc[v, 'std'])
        else:
            for v in self.perf_threshold_summary.index:
                perf[v] = {}
                perf[v]['mean'] = to_percentage(
                    self.perf_threshold_summary.loc[v, 'mean'])
                perf[v]['std'] = trunc(
                    self.perf_threshold_summary.loc[v, 'std'])
        json.dump(perf, f, indent=2)
