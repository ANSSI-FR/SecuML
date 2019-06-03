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

from secuml.core.classif.classifiers.random_forest import RandomForest

from . import SupervisedClassifierConf


class RandomForestConf(SupervisedClassifierConf):

    def __init__(self, multiclass, hyperparam_conf, logger):
        SupervisedClassifierConf.__init__(self, multiclass, hyperparam_conf,
                                          logger)
        self.accept_sparse = True

    def _get_model_class(self):
        return RandomForest

    @staticmethod
    def from_json(multiclass, hyperparam_conf, obj, logger):
        return RandomForestConf(multiclass, hyperparam_conf, logger)

    def is_probabilist(self):
        return True

    def scoring_function(self):
        return None

    def get_feature_importance(self):
        return 'score'

    @staticmethod
    def _get_hyper_desc():
        hyper = {}
        hyper['n_estimators'] = {}
        hyper['n_estimators']['values'] = {'type': int,
                                           'default': [100]}
        hyper['criterion'] = {}
        hyper['criterion']['values'] = {'choices': ['gini', 'entropy'],
                                        'default': ['gini']}
        hyper['max_depth'] = {}
        hyper['max_depth']['values'] = {'type': int,
                                        'default': [None]}
        hyper['min_samples_split'] = {}
        hyper['min_samples_split']['values'] = {'type': int,
                                                'default': [2]}
        hyper['min_samples_leaf'] = {}
        hyper['min_samples_leaf']['values'] = {'type': int,
                                               'default': [1]}
        hyper['max_features'] = {}
        hyper['max_features']['values'] = {'choices': ['sqrt', 'log2'],
                                           'default': ['sqrt']}
        hyper['max_leaf_nodes'] = {}
        hyper['max_leaf_nodes']['values'] = {'type': int,
                                             'default': [None]}
        hyper['min_impurity_decrease'] = {}
        hyper['min_impurity_decrease']['values'] = {'type': int,
                                                    'default': [0]}
        hyper['bootstrap'] = {}
        hyper['bootstrap']['values'] = {'type': bool,
                                        'default': [False]}
        hyper['oob_score'] = {}
        hyper['oob_score']['values'] = {'type': bool,
                                        'default': [False]}
        return hyper

    @staticmethod
    def gen_parser(parser):
        SupervisedClassifierConf.gen_parser(parser, RandomForestConf)

    @staticmethod
    def from_args(args, hyperparam_conf, logger):
        return RandomForestConf(args.multiclass, hyperparam_conf, logger)
