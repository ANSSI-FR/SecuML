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

import numpy as np

from secuml.core.classif.classifiers.svc import Svc
from . import SupervisedClassifierConf


class SvcConf(SupervisedClassifierConf):

    def _get_model_class(self):
        return Svc

    def is_probabilist(self):
        return False

    def scoring_function(self):
        return 'decision_function'

    def get_feature_importance(self):
        return None

    @staticmethod
    def _get_hyper_desc():
        hyper = {}
        hyper['regularization'] = {}
        hyper['regularization']['values'] = {
                                      'type': float,
                                      'default': list(10. ** np.arange(-2, 2))}
        hyper['regularization']['sklearn_name'] = 'C'
        return hyper

    @staticmethod
    def gen_parser(parser):
        SupervisedClassifierConf.gen_parser(parser, SvcConf)

    @staticmethod
    def from_args(args, hyperparam_conf, logger):
        return SvcConf(args.multiclass, hyperparam_conf, logger)

    @staticmethod
    def from_json(multiclass, hyperparam_conf, obj, logger):
        return SvcConf(multiclass, hyperparam_conf, logger)
