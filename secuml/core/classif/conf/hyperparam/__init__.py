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

from secuml.core.conf import Conf
from secuml.core.conf import exportFieldMethod

from .optim import OptimConf
from .values import Hyperparams


class HyperparamConf(Conf):

    def __init__(self, values, optim_conf, logger):
        Conf.__init__(self, logger)
        self.values = values
        self.optim_conf = optim_conf

    def get_param_grid(self):
        if self.values is None:
            return None
        return self.values.get_param_grid()

    def fields_to_export(self):
        return [('optim_conf', exportFieldMethod.obj),
                ('values', exportFieldMethod.obj)]

    @staticmethod
    def gen_parser(parser, hyperparam_desc, cv_optim, subgroup=True):
        Hyperparams.gen_parser(parser, hyperparam_desc, cv_optim,
                               subgroup=subgroup)
        if cv_optim:
            OptimConf.gen_parser(parser, subgroup=subgroup)

    @staticmethod
    def from_args(args, hyperparam_desc, cv_optim, logger):
        optim_conf = None
        if cv_optim:
            optim_conf = OptimConf.from_args(args, logger)
        values = Hyperparams.from_args(args, hyperparam_desc, cv_optim, logger)
        return HyperparamConf(values, optim_conf, logger)

    @staticmethod
    def from_json(obj, hyperparam_desc, logger):
        if obj is None:
            return None
        optim_conf = OptimConf.from_json(obj['optim_conf'], logger)
        values = Hyperparams.from_json(obj['values'], hyperparam_desc, logger)
        return HyperparamConf(values, optim_conf, logger)

    @staticmethod
    def get_default(num_folds, n_jobs, multiclass, hyperparam_desc, logger):
        optim_conf = OptimConf.get_default(num_folds, n_jobs, multiclass,
                                           logger)
        values = Hyperparams.get_default(hyperparam_desc, logger)
        return HyperparamConf(values, optim_conf, logger)
