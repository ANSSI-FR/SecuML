# SecuML
# Copyright (C) 2017  ANSSI
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

from SecuML.core.Classification.Classifiers.GradientBoosting import GradientBoosting

from . import ClassifierConfFactory
from .ClassifierConfiguration import ClassifierConfiguration
from .TestConfiguration import TestConfFactory


class GradientBoostingConfiguration(ClassifierConfiguration):

    def __init__(self, num_folds, sample_weight, families_supervision,
                 loss, learning_rate, n_estimators, max_features,
                 criterion, max_depth, min_samples_split, subsample,
                 min_samples_leaf, min_weight_fraction_leaf,
                 max_leaf_nodes, min_impurity_decrease, presort,
                 test_conf, logger=None):
        ClassifierConfiguration.__init__(self, num_folds, sample_weight,
                                         families_supervision,
                                         test_conf=test_conf,
                                         logger=logger)
        self.model_class = GradientBoosting
        self.loss = loss
        self.learning_rate = learning_rate
        self.n_estimators = n_estimators
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.subsample = subsample
        self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes
        self.min_impurity_decrease = min_impurity_decrease
        self.presort = presort

    def getModelClassName(self):
        return 'GradientBoosting'

    def generateSuffix(self):
        suffix = ClassifierConfiguration.generateSuffix(self)
        return suffix

    def getParamGrid(self):
        return None

    def setBestValues(self, grid_search):
        return

    def getBestValues(self):
        return None

    @staticmethod
    def fromJson(obj):
        test_conf = TestConfFactory.getFactory().fromJson(obj['test_conf'])
        conf = GradientBoostingConfiguration(obj['num_folds'],
                                             obj['sample_weight'],
                                             obj['families_supervision'],
                                             obj['loss'],
                                             obj['learning_rate'],
                                             obj['n_estimators'],
                                             obj['max_features'],
                                             obj['criterion'],
                                             obj['max_depth'],
                                             obj['min_samples_split'],
                                             obj['subsample'],
                                             obj['min_samples_leaf'],
                                             obj['min_weight_fraction_leaf'],
                                             obj['max_leaf_nodes'],
                                             obj['min_impurity_decrease'],
                                             obj['presort'],
                                             test_conf)
        return conf

    def toJson(self):
        conf = ClassifierConfiguration.toJson(self)
        conf['__type__'] = 'GradientBoostingConfiguration'
        conf['sample_weight'] = self.sample_weight
        conf['families_supervision'] = self.families_supervision
        conf['loss'] = self.loss
        conf['learning_rate'] = self.learning_rate
        conf['n_estimators'] = self.n_estimators
        conf['max_features'] = self.max_features
        conf['criterion'] = self.criterion
        conf['max_depth'] = self.max_depth
        conf['min_samples_split'] = self.min_samples_split
        conf['subsample'] = self.subsample
        conf['min_samples_leaf'] = self.min_samples_leaf
        conf['min_weight_fraction_leaf'] = self.min_weight_fraction_leaf
        conf['max_leaf_nodes'] = self.max_leaf_nodes
        conf['min_impurity_decrease'] = self.min_impurity_decrease
        conf['presort'] = self.presort
        return conf

    def probabilistModel(self):
        return True

    def semiSupervisedModel(self):
        return False

    def featureImportance(self):
        return 'score'

    @staticmethod
    def generateParser(parser):
        ClassifierConfiguration.generateParser(parser)
        help_message = 'See the scikit-learn documentation.'
        parser.add_argument('--loss',
                            choices=['deviance', 'exponential'],
                            default='deviance',
                            help=help_message)
        parser.add_argument('--learning-rate',
                            type=float,
                            default=0.1,
                            help=help_message)
        parser.add_argument('--n-estimators',
                            type=int,
                            default=10,
                            help=help_message)
        parser.add_argument('--max-features',
                            type=int,
                            default=None,
                            help=help_message)
        parser.add_argument('--criterion',
                            choices=['msa', 'mae', 'friedman_mse'],
                            default='friedman_mse',
                            help=help_message)
        parser.add_argument('--max-depth',
                            type=int,
                            default=None,
                            help=help_message)
        parser.add_argument('--min-samples-split',
                            type=int,
                            default=2,
                            help=help_message)
        parser.add_argument('--subsample',
                            type=float,
                            default=0.1,
                            help=help_message)
        parser.add_argument('--min-samples-leaf',
                            type=int,
                            default=1,
                            help=help_message)
        parser.add_argument('--min-weight-fraction-leaf',
                            type=float,
                            default=0,
                            help=help_message)
        parser.add_argument('--max-leaf_nodes',
                            type=int,
                            default=None,
                            help=help_message)
        parser.add_argument('--min-impurity-decrease',
                            type=float,
                            default=0,
                            help=help_message)
        parser.add_argument('--presort',
                            type=bool,
                            default=True)

    @staticmethod
    def generateParamsFromArgs(args):
        params = ClassifierConfiguration.generateParamsFromArgs(args)
        params['sample_weight'] = args.sample_weight
        params['loss'] = args.loss
        params['learning_rate'] = args.learning_rate
        params['n_estimators'] = args.n_estimators
        params['max_features'] = args.max_features
        params['criterion'] = args.criterion
        params['max_depth'] = args.max_depth
        params['min_samples_split'] = args.min_samples_split
        params['subsample'] = args.subsample
        params['min_samples_leaf'] = args.min_samples_leaf
        params['min_weight_fraction_leaf'] = args.min_weight_fraction_leaf
        params['max_leaf_nodes'] = args.max_leaf_nodes
        params['min_impurity_decrease'] = args.min_impurity_decrease
        params['presort'] = args.presort
        return params


ClassifierConfFactory.getFactory().registerClass('GradientBoostingConfiguration',
                                                 GradientBoostingConfiguration)
