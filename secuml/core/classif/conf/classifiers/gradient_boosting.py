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

from secuml.core.classif.classifiers.gradient_boosting import GradientBoosting
from . import SupervisedClassifierConf


class GradientBoostingConf(SupervisedClassifierConf):

    def _get_model_class(self):
        return GradientBoosting

    @staticmethod
    def from_json(multiclass, hyperparam_conf, obj, logger):
        return GradientBoostingConf(multiclass, hyperparam_conf, logger)

    def is_probabilist(self):
        return True

    def scoring_function(self):
        return 'decision_function'

    def get_feature_importance(self):
        return 'score'

    @staticmethod
    def _get_hyper_desc():
        hyper = {}
        hyper['loss'] = {}
        hyper['loss']['values'] = {'choices': ['deviance', 'exponential'],
                                   'default': ['deviance', 'exponential']}
        hyper['learning_rate'] = {}
        hyper['learning_rate']['values'] = {'type': float,
                                            'default': [0.1]}
        hyper['n_estimators'] = {}
        hyper['n_estimators']['values'] = {'type': int,
                                           'default': [10, 100, 1000]}
        hyper['criterion'] = {}
        hyper['criterion']['values'] = {'choices': ['mse', 'mae',
                                                    'friedman_mse'],
                                        'default': ['mse', 'mae',
                                                    'friedman_mse']}
        hyper['max_depth'] = {}
        hyper['max_depth']['values'] = {'type': int,
                                        'default': [5, 10, 15, 20, None]}
        hyper['min_samples_split'] = {}
        hyper['min_samples_split']['values'] = {'type': int,
                                                'default': [2]}
        hyper['min_samples_leaf'] = {}
        hyper['min_samples_leaf']['values'] = {'type': int,
                                               'default': [1]}
        hyper['max_features'] = {}
        hyper['max_features']['values'] = {'default': ['sqrt', 'log2', None]}
        hyper['max_leaf_nodes'] = {}
        hyper['max_leaf_nodes']['values'] = {'type': int,
                                             'default': [None]}
        hyper['min_impurity_decrease'] = {}
        hyper['min_impurity_decrease']['values'] = {'type': int,
                                                    'default': [0]}
        hyper['subsample'] = {}
        hyper['subsample']['values'] = {'type': float,
                                        'default': [0.1]}
        hyper['presort'] = {}
        hyper['presort']['values'] = {'type': bool,
                                      'default': [True]}
        return hyper

    @staticmethod
    def gen_parser(parser):
        SupervisedClassifierConf.gen_parser(
                                         parser,
                                         GradientBoostingConf._get_hyper_desc())

    @staticmethod
    def from_args(args, hyperparam_conf, logger):
        return GradientBoostingConf(args.multiclass, hyperparam_conf, logger)
