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

import numpy as np
from sklearn.metrics import make_scorer

from SecuML.core.classification.monitoring.FalseDiscoveryRecallCurve \
        import interpRecall
from SecuML.core.Conf import exportFieldMethod

from .ObjectiveFuncConf import ObjectiveFuncConf
from . import ObjectiveFuncConfFactory

def detectionRateAtFDR(ground_truth, scores, far):
    precision_sample = np.linspace(0, 1, 101)
    recall, _ = interpRecall(ground_truth, scores, precision_sample)
    return recall[100 - int(far*100)]

class DrAtFarConf(ObjectiveFuncConf):

    def __init__(self, far, logger):
        ObjectiveFuncConf.__init__(self, logger)
        self.far = far

    def getScoringMethod(self):
        return make_scorer(detectionRateAtFDR,
                           greater_is_better=True,
                           needs_threshold=True,
                           far=self.far)

    def fieldsToExport(self):
        fields = ObjectiveFuncConf.fieldsToExport(self)
        fields.extend([('far', exportFieldMethod.primitive)])

    @staticmethod
    def generateParser(parser):
        parser.add_argument('--far',
                            type=float,
                            default=0.05,
                            help='False Alarm Rate (FAR) for which the '
                                 'Detection Rate (DR) should be optimized.')

    @staticmethod
    def from_json(obj, logger):
        return DrAtFarConf(obj['far'], logger)

    @staticmethod
    def fromArgs(args, logger):
        return DrAtFarConf(args.far, logger)


ObjectiveFuncConfFactory.getFactory().registerClass('DrAtFarConf',
                                                    DrAtFarConf)
