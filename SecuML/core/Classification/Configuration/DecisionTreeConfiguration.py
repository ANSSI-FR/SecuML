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

from SecuML.core.Classification.Classifiers.DecisionTree import DecisionTree

from . import ClassifierConfFactory
from .ClassifierConfiguration import ClassifierConfiguration
from .TestConfiguration import TestConfFactory


class DecisionTreeConfiguration(ClassifierConfiguration):

    def __init__(self, n_jobs, num_folds, sample_weight, families_supervision,
                 criterion, splitter, max_depth, min_samples_split,
                 min_samples_leaf, min_weight_fraction_leaf, max_features,
                 max_leaf_nodes, min_impurity_decrease, test_conf,
                 logger=None):
        ClassifierConfiguration.__init__(self, n_jobs, num_folds, sample_weight,
                                         families_supervision,
                                         test_conf=test_conf,
                                         logger=logger)
        self.model_class = DecisionTree
        self.criterion = criterion
        self.splitter = splitter
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes
        self.min_impurity_decrease = min_impurity_decrease

    def getModelClassName(self):
        return 'DecisionTree'

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
    def fromJson(obj, logger=None):
        test_conf = TestConfFactory.getFactory().fromJson(obj['test_conf'],
                                                          logger=logger)
        conf = DecisionTreeConfiguration(obj['n_jobs'], obj['num_folds'],
                                         obj['sample_weight'],
                                         obj['families_supervision'],
                                         obj['criterion'],
                                         obj['splitter'],
                                         obj['max_depth'],
                                         obj['min_samples_split'],
                                         obj['min_samples_leaf'],
                                         obj['min_weight_fraction_leaf'],
                                         obj['max_features'],
                                         obj['max_leaf_nodes'],
                                         obj['min_impurity_decrease'],
                                         test_conf,
                                         logger=logger)
        return conf

    def toJson(self):
        conf = ClassifierConfiguration.toJson(self)
        conf['__type__'] = 'DecisionTreeConfiguration'
        conf['criterion'] = self.criterion
        conf['splitter'] = self.splitter
        conf['max_depth'] = self.max_depth
        conf['min_samples_split'] = self.min_samples_split
        conf['min_samples_leaf'] = self.min_samples_leaf
        conf['min_weight_fraction_leaf'] = self.min_weight_fraction_leaf
        conf['max_features'] = self.max_features
        conf['max_leaf_nodes'] = self.max_leaf_nodes
        conf['min_impurity_decrease'] = self.min_impurity_decrease
        return conf

    def probabilistModel(self):
        return False

    def semiSupervisedModel(self):
        return False

    def featureImportance(self):
        return 'score'

    @staticmethod
    def generateParser(parser):
        ClassifierConfiguration.generateParser(parser)
        help_message = 'See the scikit-learn documentation.'
        parser.add_argument('--criterion',
                            choices=['gini', 'entropy'],
                            default='gini',
                            help=help_message)
        parser.add_argument('--splitter',
                            choices=['best', 'random'],
                            default='best',
                            help=help_message)
        parser.add_argument('--max-depth',
                            type=int,
                            default=None,
                            help=help_message)
        parser.add_argument('--min-samples-split',
                            type=int,
                            default=2,
                            help=help_message)
        parser.add_argument('--min-samples-leaf',
                            type=int,
                            default=1,
                            help=help_message)
        parser.add_argument('--min-weight-fraction-leaf',
                            type=float,
                            default=0,
                            help=help_message)
        parser.add_argument('--max-features',
                            type=int,
                            default=None,
                            help=help_message)
        parser.add_argument('--max-leaf_nodes',
                            type=int,
                            default=None,
                            help=help_message)
        parser.add_argument('--min-impurity-decrease',
                            type=float,
                            default=0,
                            help=help_message)

    @staticmethod
    def generateParamsFromArgs(args, logger=None):
        params = ClassifierConfiguration.generateParamsFromArgs(args,
                                                                logger=logger)
        params['criterion'] = args.criterion
        params['splitter'] = args.splitter
        params['max_depth'] = args.max_depth
        params['min_samples_split'] = args.min_samples_split
        params['min_samples_leaf'] = args.min_samples_leaf
        params['min_weight_fraction_leaf'] = args.min_weight_fraction_leaf
        params['max_features'] = args.max_features
        params['max_leaf_nodes'] = args.max_leaf_nodes
        params['min_impurity_decrease'] = args.min_impurity_decrease
        return params


ClassifierConfFactory.getFactory().registerClass('DecisionTreeConfiguration',
                                                 DecisionTreeConfiguration)
