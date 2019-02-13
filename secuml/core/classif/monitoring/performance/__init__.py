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

from .confusion_matrix import ConfusionMatrix
from .binary_errors import BinaryErrors
from .binary_perf_indicators import BinaryPerfIndicators
from .multiclass_errors import MulticlassErrors
from .multiclass_perf_indicators import MulticlassPerfIndicators
from .fdr_tpr_curve import FdrTprCurve
from .roc_curve import RocCurve


class PerformanceMonitoring(object):

    def __init__(self, num_folds, conf):
        self.conf = conf
        if self.conf.multiclass:
            self.perf_indicators = MulticlassPerfIndicators(num_folds)
            self.errors = MulticlassErrors()
        else:
            self.perf_indicators = BinaryPerfIndicators(num_folds,
                                                        conf.is_probabilist())
            self.errors = BinaryErrors(conf)
            self.confusion_matrix = ConfusionMatrix()
            self.roc = RocCurve(num_folds, conf)
            self.fdr_tpr_curve = FdrTprCurve(num_folds, conf)

    def add_fold(self, fold, predictions):
        self.perf_indicators.add_fold(fold, predictions)
        self.errors.add_fold(predictions)
        if not self.conf.multiclass:
            self.confusion_matrix.add_fold(predictions)
            self.roc.add_fold(fold, predictions)
            self.fdr_tpr_curve.add_fold(fold, predictions)

    def final_computations(self):
        self.perf_indicators.final_computations()

    def display(self, directory):
        with open(path.join(directory, 'perf_indicators.json'), 'w') as f:
            self.perf_indicators.to_json(f)
        with open(path.join(directory, 'errors.json'), 'w') as f:
            self.errors.to_json(f)
        if not self.conf.multiclass:
            with open(path.join(directory, 'confusion_matrix.json'), 'w') as f:
                self.confusion_matrix.to_json(f)
            self.roc.display(directory)
            self.fdr_tpr_curve.display(directory)
