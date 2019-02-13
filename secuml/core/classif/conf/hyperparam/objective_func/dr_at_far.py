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

from secuml.core.classif.monitoring.performance.fdr_tpr_curve \
        import interp_recall
from secuml.core.conf import exportFieldMethod

from . import ObjectiveFuncConf


def detection_rate_at_fdr(ground_truth, scores, far):
    precision_sample = np.linspace(0, 1, 101)
    recall, _ = interp_recall(ground_truth, scores, precision_sample)
    return recall[100 - int(far*100)]


class DrAtFarConf(ObjectiveFuncConf):

    def __init__(self, far, logger):
        ObjectiveFuncConf.__init__(self, logger)
        self.far = far

    def get_scoring_method(self):
        return make_scorer(detection_rate_at_fdr,
                           greater_is_better=True,
                           needs_threshold=True,
                           far=self.far)

    def fields_to_export(self):
        fields = ObjectiveFuncConf.fields_to_export(self)
        fields.extend([('far', exportFieldMethod.primitive)])

    @staticmethod
    def gen_parser(parser):
        parser.add_argument('--far',
                            type=float,
                            default=0.05,
                            help='False Alarm Rate (FAR) for which the '
                                 'Detection Rate (DR) should be optimized.')

    @staticmethod
    def from_json(obj, logger):
        return DrAtFarConf(obj['far'], logger)

    @staticmethod
    def from_args(args, logger):
        return DrAtFarConf(args.far, logger)
