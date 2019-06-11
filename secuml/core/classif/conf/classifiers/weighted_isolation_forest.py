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

from secuml.core.classif.classifiers.weighted_isolation_forest \
        import WeightedIsolationForest
from secuml.core.conf import exportFieldMethod
from . import SemiSupervisedClassifierConf


class WeightedIsolationForestConf(SemiSupervisedClassifierConf):

    def __init__(self, hyper_conf, logger, n_jobs=-1):
        SemiSupervisedClassifierConf.__init__(self, False, hyper_conf, logger)
        self.accept_sparse = True
        self.n_jobs = n_jobs

    def _get_model_class(self):
        return WeightedIsolationForest

    def fields_to_export(self):
        fields = SemiSupervisedClassifierConf.fields_to_export(self)
        fields.append(('n_jobs', exportFieldMethod.primitive))
        return fields

    @staticmethod
    def from_json(multiclass, hyperparam_conf, obj, logger):
        return WeightedIsolationForestConf(hyperparam_conf, logger,
                                           n_jobs=obj['n_jobs'])

    def is_probabilist(self):
        return False

    def get_feature_importance(self):
        return None

    def scoring_function(self):
        return 'decision_function'

    @staticmethod
    def _get_hyper_desc():
        hyper = {}
        hyper['eta'] = {}
        hyper['eta']['values'] = {'type': float,
                                  'default': 1.}
        hyper['n_estimators'] = {}
        hyper['n_estimators']['values'] = {'type': int,
                                           'default': 100}
        hyper['max_samples'] = {}
        hyper['max_samples']['values'] = {'type': str,
                                          'default': 'auto'}
        hyper['max_features'] = {}
        hyper['max_features']['values'] = {'type': float,
                                           'default': 1.0}
        return hyper

    @staticmethod
    def gen_parser(parser):
        SemiSupervisedClassifierConf.gen_parser(parser,
                                                WeightedIsolationForestConf,
                                                multiclass=False)
        parser.add_argument('--n_jobs',
                            type=int,
                            default=-1,
                            help='Number of CPU cores used to train the '
                                 'model. '
                                 'If given a value of -1, all cores are used. '
                                 'Default: -1.')

    @staticmethod
    def from_args(args, hyperparam_conf, logger):
        return WeightedIsolationForestConf(hyperparam_conf, logger,
                                           n_jobs=args.n_jobs)
