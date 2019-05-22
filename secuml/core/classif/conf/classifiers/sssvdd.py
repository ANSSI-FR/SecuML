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
from secuml.core.conf import exportFieldMethod
from . import SemiSupervisedClassifierConf


class SssvddConf(SemiSupervisedClassifierConf):

    def __init__(self, hyperparam_conf, logger, nu_u=1.0, nu_l=1.0, kappa=1.0):
        SemiSupervisedClassifierConf.__init__(self, False, hyperparam_conf,
                                              logger)
        self.nu_u = nu_u
        self.nu_l = nu_l
        self.kappa = kappa

    def _get_model_class(self):
        return Sssvdd

    def is_probabilist(self):
        return False

    def scoring_function(self):
        return 'decision_function'

    def get_feature_importance(self):
        return None

    @staticmethod
    def _get_hyper_desc():
        return None

    def fields_to_export(self):
        fields = SemiSupervisedClassifierConf.fields_to_export(self)
        fields.append(('nu_u', exportFieldMethod.primitive))
        fields.append(('nu_l', exportFieldMethod.primitive))
        fields.append(('kappa', exportFieldMethod.primitive))
        return fields

    @staticmethod
    def from_json(multiclass, hyperparam_conf, obj, logger):
        return SssvddConf(hyperparam_conf, logger, nu_u=obj['nu_u'],
                          nu_l=obj['nu_l'], kappa=obj['kappa'])

    @staticmethod
    def gen_parser(parser):
        SemiSupervisedClassifierConf.gen_parser(parser, SssvddConf,
                                                multiclass=False)
        parser.add_argument('--nu-l', type=float, default=1.0,
                            help='Default: 1.0')
        parser.add_argument('--nu-u', type=float, default=1.0,
                            help='Default: 1.0')
        parser.add_argument('--kappa', type=float, default=1.0,
                            help='Default: 1.0')

    @staticmethod
    def from_args(args, hyperparam_conf, logger):
        return SssvddConf(hyperparam_conf, logger, nu_u=args.nu_u,
                          nu_l=args.nu_l, kappa=args.kappa)
