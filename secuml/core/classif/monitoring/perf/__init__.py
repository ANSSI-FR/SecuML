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

import os.path as path

from .binary_indicators import BinaryIndicators
from .confusion_matrix import ConfusionMatrix
from .fdr_tpr_curve import FdrTprCurve
from .multiclass_indicators import MulticlassIndicators
from .roc_curve import RocCurve


class PerformanceMonitoring(object):

    def __init__(self, num_folds, conf):
        self.conf = conf
        if self.conf.multiclass:
            self.perf_indicators = MulticlassIndicators(num_folds)
        else:
            self.perf_indicators = BinaryIndicators(num_folds,
                                                    conf.is_probabilist())
            self.confusion_matrix = ConfusionMatrix()
            self.roc = RocCurve(num_folds, conf.is_probabilist())
            self.fdr_tpr_curve = FdrTprCurve(num_folds, conf.is_probabilist())

    def add_fold(self, fold, predictions):
        self.perf_indicators.add_fold(fold, predictions)
        if not self.conf.multiclass:
            self.confusion_matrix.add_fold(predictions)
            self.roc.add_fold(fold, predictions)
            self.fdr_tpr_curve.add_fold(fold, predictions)

    def final_computations(self):
        self.perf_indicators.final_computations()

    def display(self, directory):
        with open(path.join(directory, 'perf_indicators.json'), 'w') as f:
            self.perf_indicators.to_json(f)
        if not self.conf.multiclass:
            self.confusion_matrix.display(directory)
            self.roc.display(directory)
            self.fdr_tpr_curve.display(directory)
