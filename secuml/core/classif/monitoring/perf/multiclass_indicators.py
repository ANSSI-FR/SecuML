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

from secuml.core.clustering.monitoring.perf_indicators \
        import PerformanceIndicators
from secuml.core.tools.float import to_percentage, trunc


class MulticlassIndicators(object):

    def __init__(self, num_folds):
        self.num_folds = num_folds
        self.accuracy = [0] * num_folds
        self.f1_micro = [0] * num_folds
        self.f1_macro = [0] * num_folds
        self.clustering_perf = PerformanceIndicators()
        self.ground_truth = []
        self.predictions = []

    def add_fold(self, fold_id, predictions):
        self._set_fscores(fold_id, predictions)
        self._set_accuracy(fold_id, predictions)
        self._update_gt_predictions(predictions)

    def get_accuracy(self):
        return self.accuracy_mean

    def final_computations(self):
        self.accuracy_mean = np.mean(self.accuracy)
        self.accuracy_std = np.std(self.accuracy)
        self.f1_micro_mean = np.mean(self.f1_micro)
        self.f1_micro_std = np.std(self.f1_micro)
        self.f1_macro_mean = np.mean(self.f1_macro)
        self.f1_macro_std = np.std(self.f1_macro)
        self.clustering_perf.gen_eval(self.ground_truth, self.predictions)

    def to_json(self, f):
        perf = {}
        perf['accuracy'] = {'mean': to_percentage(self.accuracy_mean),
                            'std': trunc(self.accuracy_std)}
        perf['f1_micro'] = {'mean': to_percentage(self.f1_micro_mean),
                            'std': trunc(self.f1_micro_std)}
        perf['f1_macro'] = {'mean': to_percentage(self.f1_macro_mean),
                            'std': trunc(self.f1_macro_std)}
        perf['clustering_perf'] = self.clustering_perf.to_json()
        json.dump(perf, f, indent=2)

    def get_csv_header(self):
        return ['accuracy', 'f1-micro', 'f1-macro']

    def get_csv_line(self):
        return [self.accuracy_mean, self.f1_micro_mean, self.f1_macro_mean]

    def _set_fscores(self, fold_id, predictions):
        diff = set(predictions.ground_truth) - set(predictions.values)
        if predictions.num_instances() > 0 and len(diff) == 0:
            self.f1_micro[fold_id] = f1_score(predictions.ground_truth,
                                              predictions.values,
                                              average='micro')
            self.f1_macro[fold_id] = f1_score(predictions.ground_truth,
                                              predictions.values,
                                              average='macro')
        else:
            self.f1_micro[fold_id] = 0
            self.f1_macro[fold_id] = 0

    def _set_accuracy(self, fold_id, predictions):
        if predictions.num_instances() == 0:
            self.accuracy[fold_id] = 0
        else:
            self.accuracy[fold_id] = accuracy_score(predictions.ground_truth,
                                                    predictions.values)

    def _update_gt_predictions(self, predictions):
        self.ground_truth.extend(predictions.ground_truth)
        self.predictions.extend(predictions.values)
