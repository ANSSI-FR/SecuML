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

import os.path as path

from secuml.core.data.predictions import InconsistentPredictions

from .binary_indicators import BinaryIndicators
from .confusion_matrix import ConfusionMatrix
from .fdr_tpr_curve import FdrTprCurve
from .multiclass_indicators import MulticlassIndicators
from .roc_curve import RocCurve


class PerformanceMonitoring(object):

    def __init__(self, num_folds=1):
        self.num_folds = num_folds
        self.pred_info = None
        # Monitoring
        self.perf_indicators = None
        self.confusion_matrix = None
        self.roc = None
        self.fdr_tpr_curve = None

    def init(self, predictions):
        self.pred_info = predictions.info
        if self.pred_info.multiclass:
            self.perf_indicators = MulticlassIndicators(self.num_folds)
        else:
            self.perf_indicators = BinaryIndicators(self.num_folds,
                                                    self.pred_info.with_probas,
                                                    self.pred_info.with_scores)
            self.confusion_matrix = ConfusionMatrix()
            if self.pred_info.with_probas or self.pred_info.with_scores:
                self.roc = RocCurve(self.num_folds, self.pred_info.with_probas)
                self.fdr_tpr_curve = FdrTprCurve(self.num_folds,
                                                 self.pred_info.with_probas)

    def add_fold(self, predictions, fold_id=0):
        if self.pred_info is None:
            self.init(predictions)
        else:
            if not self.pred_info.equal(predictions.info):
                raise InconsistentPredictions()
        self.perf_indicators.add_fold(fold_id, predictions)
        if not self.pred_info.multiclass:
            self.confusion_matrix.add_fold(predictions)
            if self.roc is not None:
                self.roc.add_fold(fold_id, predictions)
            if self.fdr_tpr_curve is not None:
                self.fdr_tpr_curve.add_fold(fold_id, predictions)

    def final_computations(self):
        self.perf_indicators.final_computations()

    def display(self, directory):
        with open(path.join(directory, 'perf_indicators.json'), 'w') as f:
            self.perf_indicators.to_json(f)
        if not self.pred_info.multiclass:
            self.confusion_matrix.display(directory)
            if self.roc is not None:
                self.roc.display(directory)
            if self.fdr_tpr_curve is not None:
                self.fdr_tpr_curve.display(directory)
