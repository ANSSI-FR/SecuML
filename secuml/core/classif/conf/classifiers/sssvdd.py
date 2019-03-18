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

from secuml.core.classif.classifiers.sssvdd import Sssvdd
from . import SemiSupervisedClassifierConf


class SssvddConf(SemiSupervisedClassifierConf):

    def __init__(self, hyperparam_conf, logger):
        SemiSupervisedClassifierConf.__init__(self, False, hyperparam_conf,
                                              logger)

    def _get_model_class(self):
        return Sssvdd

    def is_probabilist(self):
        return False

    def scoring_function(self):
        return None

    def get_feature_importance(self):
        return None

    @staticmethod
    def _get_hyper_desc():
        return None

    @staticmethod
    def from_json(multiclass, hyperparam_conf, obj, logger):
        return SssvddConf(hyperparam_conf, logger)

    @staticmethod
    def gen_parser(parser):
        SemiSupervisedClassifierConf.gen_parser(parser, SssvddConf)

    @staticmethod
    def from_args(args, hyperparam_conf, logger):
        return SssvddConf(hyperparam_conf, logger)
