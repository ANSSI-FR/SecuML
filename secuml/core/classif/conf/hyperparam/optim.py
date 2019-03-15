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
from secuml.core.conf import register_submodules

from . import objective_func
from .objective_func import ObjectiveFuncConf
from .objective_func.accuracy import AccuracyConf
from .objective_func.roc_auc import RocAucConf


class OptimConf(Conf):

    def __init__(self, num_folds, n_jobs, obj_func, logger):
        Conf.__init__(self, logger)
        self.num_folds = num_folds
        self.n_jobs = n_jobs
        self.objective_func = obj_func

    def get_scoring_method(self):
        return self.objective_func.get_scoring_method()

    def get_exp_name(self):
        return ''

    def fields_to_export(self):
        return [('num_folds', exportFieldMethod.primitive),
                ('n_jobs', exportFieldMethod.primitive),
                ('objective_func', exportFieldMethod.obj)]

    @staticmethod
    def gen_parser(parser, subgroup=True):
        group = parser
        if subgroup:
            group = parser.add_argument_group('Hyperparameters optimization')
        group.add_argument(
                 '--n-jobs',
                 type=int,
                 default=-1,
                 help='Number of CPU cores used when parallelizing the cross '
                      'validation looking for the best hyper-parameters. '
                      'If given a value of -1, all cores are used. '
                      'Default: -1.')
        group.add_argument(
                 '--num-folds',
                 type=int,
                 default=4,
                 help='Number of folds built in the cross validation looking '
                      'for the best hyper-parameters. '
                      'Default: 4.')
        ObjectiveFuncConf.gen_parser(group)

    @staticmethod
    def from_json(obj, logger):
        if obj is None:
            return None
        factory = objective_func.get_factory()
        obj_func_conf = factory.from_json(obj['objective_func'], logger)
        return OptimConf(obj['num_folds'], obj['n_jobs'], obj_func_conf,
                         logger)

    @staticmethod
    def from_args(args, logger):
        factory = objective_func.get_factory()
        if args.multiclass:
            obj_func_conf = factory.from_args('Accuracy', args, logger)
        else:
            obj_func_conf = factory.from_args(args.objective_func, args,
                                              logger)
        return OptimConf(args.num_folds, args.n_jobs, obj_func_conf, logger)

    @staticmethod
    def get_default(num_folds, n_jobs, multiclass, logger):
        if num_folds is None:
            num_folds = 4
        if n_jobs is None:
            n_jobs = 1
        if multiclass:
            scoring = AccuracyConf
        else:
            scoring = RocAucConf
        return OptimConf(num_folds, n_jobs, scoring(logger), logger)


register_submodules(objective_func, objective_func.get_factory())
