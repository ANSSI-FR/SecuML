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

from SecuML.core.Conf import Conf
from SecuML.core.Conf import exportFieldMethod

from .ObjectiveFuncConf import ObjectiveFuncConf
from . import ObjectiveFuncConfFactory


class HyperparamOptimConf(Conf):

    def __init__(self, num_folds, n_jobs, objective_func, logger):
        Conf.__init__(self, logger)
        self.num_folds = num_folds
        self.n_jobs = n_jobs
        self.objective_func = objective_func

    def getScoringMethod(self):
        return self.objective_func.getScoringMethod()

    def get_exp_name(self):
        return ''

    def fieldsToExport(self):
        return [('num_folds', exportFieldMethod.primitive),
                ('n_jobs', exportFieldMethod.primitive),
                ('objective_func', exportFieldMethod.obj),]

    @staticmethod
    def generateParser(parser, subgroup=True):
        if subgroup:
            hyperparams_group = parser.add_argument_group('Hyperparameters '
                                                      'optimization parameters')
        else:
            hyperparams_group = parser
        hyperparams_group.add_argument('--n-jobs',
                 type=int,
                 default=-1,
                 help='Number of CPU cores used when parallelizing the cross '
                      'validation looking for the best hyper-parameters. '
                      'If given a value of -1, all cores are used. '
                      'Default: -1.')
        hyperparams_group.add_argument('--num-folds',
                 type=int,
                 default=4,
                 help='Number of folds built in the cross validation looking '
                      'for the best hyper-parameters. '
                      'Default: 4.')
        ObjectiveFuncConf.generateParser(hyperparams_group)

    @staticmethod
    def from_json(obj, logger):
        factory = ObjectiveFuncConfFactory.getFactory()
        objective_func = factory.from_json(obj['objective_func'],
                                          logger)
        return HyperparamOptimConf(obj['num_folds'], obj['n_jobs'],
                                   objective_func, logger)

    @staticmethod
    def fromArgs(args, logger):
        factory = ObjectiveFuncConfFactory.getFactory()
        objective_func = factory.fromArgs(args.objective_func, args,
                                          logger)
        conf = HyperparamOptimConf(args.num_folds,
                                   args.n_jobs,
                                   objective_func,
                                   logger)
        return conf
