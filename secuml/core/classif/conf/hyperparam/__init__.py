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

from secuml.core.conf import Conf
from secuml.core.conf import exportFieldMethod

from .optim import OptimConf
from .values import Hyperparams


def get_model_hyperparam_desc(model_class):
    if model_class is None:
        return None
    return model_class._get_hyper_desc()


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
    def gen_parser(parser, model_class, cv_optim, subgroup=True):
        hyperparam_desc = get_model_hyperparam_desc(model_class)
        Hyperparams.gen_parser(parser, hyperparam_desc, cv_optim,
                               subgroup=subgroup)
        if cv_optim:
            OptimConf.gen_parser(parser, subgroup=subgroup)

    @staticmethod
    def from_args(args, model_class, cv_optim, logger):
        optim_conf = None
        if cv_optim:
            optim_conf = OptimConf.from_args(args, logger)
        hyperparam_desc = get_model_hyperparam_desc(model_class)
        values = Hyperparams.from_args(args, hyperparam_desc, cv_optim, logger)
        return HyperparamConf(values, optim_conf, logger)

    @staticmethod
    def from_json(obj, model_class, logger):
        if obj is None:
            return None
        optim_conf = OptimConf.from_json(obj['optim_conf'], logger)
        hyperparam_desc = get_model_hyperparam_desc(model_class)
        values = Hyperparams.from_json(obj['values'], hyperparam_desc, logger)
        return HyperparamConf(values, optim_conf, logger)

    @staticmethod
    def get_default(num_folds, n_jobs, multiclass, hyperparam_desc, logger):
        optim_conf = OptimConf.get_default(num_folds, n_jobs, multiclass,
                                           logger)
        values = Hyperparams.get_default(hyperparam_desc, logger)
        return HyperparamConf(values, optim_conf, logger)
