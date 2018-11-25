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

from .ConfusionMatrix import ConfusionMatrix
from .BinaryErrors import BinaryErrors
from .BinaryPerfIndicators import BinaryPerfIndicators
from .MulticlassErrors import MulticlassErrors
from .MulticlassPerfIndicators import MulticlassPerfIndicators
from .FalseDiscoveryRecallCurve import FalseDiscoveryRecallCurve
from .ROC import ROC


class PerformanceMonitoring(object):

    def __init__(self, num_folds, conf):
        self.conf = conf
        if self.conf.families_supervision:
            self.perf_indicators = MulticlassPerfIndicators(num_folds)
            self.errors = MulticlassErrors()
        else:
            self.perf_indicators = BinaryPerfIndicators(num_folds,
                                                        conf.probabilistModel())
            self.errors = BinaryErrors(conf)
            self.confusion_matrix = ConfusionMatrix()
            self.roc = ROC(num_folds, conf)
            self.false_disc_recall_curve = FalseDiscoveryRecallCurve(num_folds,
                                                                     conf)

    def addFold(self, fold, predictions):
        self.perf_indicators.addFold(fold, predictions)
        self.errors.addFold(predictions)
        if not self.conf.families_supervision:
            self.confusion_matrix.addFold(predictions)
            self.roc.addFold(fold, predictions)
            self.false_disc_recall_curve.addFold(fold, predictions)

    def finalComputations(self):
        self.perf_indicators.finalComputations()

    def display(self, directory):
        with open(path.join(directory, 'perf_indicators.json'), 'w') as f:
            self.perf_indicators.to_json(f)
        with open(path.join(directory, 'errors.json'), 'w') as f:
            self.errors.to_json(f)
        if not self.conf.families_supervision:
            with open(path.join(directory, 'confusion_matrix.json'), 'w') as f:
                self.confusion_matrix.to_json(f)
            self.roc.display(directory)
            self.false_disc_recall_curve.display(directory)
