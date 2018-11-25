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

from SecuML.core.classification.classifiers.GradientBoosting \
        import GradientBoosting
from SecuML.core.Conf import exportFieldMethod

from . import ClassifierConfFactory
from .ClassifierConf import ClassifierConf


class GradientBoostingConf(ClassifierConf):

    def __init__(self, sample_weight, families_supervision,
                 loss, learning_rate, n_estimators, max_features,
                 criterion, max_depth, min_samples_split, subsample,
                 min_samples_leaf, min_weight_fraction_leaf,
                 max_leaf_nodes, min_impurity_decrease, presort,
                 hyperparams_optim_conf, logger):
        ClassifierConf.__init__(self, sample_weight,
                                families_supervision,
                                hyperparams_optim_conf,
                                logger)
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

    def getParamGrid(self):
        return None

    def setBestValues(self, grid_search):
        return

    def getBestValues(self):
        return None

    @staticmethod
    def from_json(obj, logger):
        hyper_conf = ClassifierConf.hyperparamConfFromJson(obj, logger)
        conf = GradientBoostingConf(obj['sample_weight'],
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
                                    hyper_conf,
                                    logger)
        return conf

    @staticmethod
    def fromArgs(args, logger):
        hyper_conf = ClassifierConf.hyperparamConfFromArgs(args, logger)
        return GradientBoostingConf(False,
                                    False,
                                    args.loss,
                                    args.learning_rate,
                                    args.n_estimators,
                                    args.max_features,
                                    args.criterion,
                                    args.max_depth,
                                    args.min_samples_split,
                                    args.subsample,
                                    args.min_samples_leaf,
                                    args.min_weight_fraction_leaf,
                                    args.max_leaf_nodes,
                                    args.min_impurity_decrease,
                                    args.presort,
                                    hyper_conf,
                                    logger)


    def fieldsToExport(self):
        fields = ClassifierConf.fieldsToExport(self)
        fields.extend([('loss', exportFieldMethod.primitive),
                     ('learning_rate', exportFieldMethod.primitive),
                     ('n_estimators', exportFieldMethod.primitive),
                     ('max_features', exportFieldMethod.primitive),
                     ('criterion', exportFieldMethod.primitive),
                     ('max_depth', exportFieldMethod.primitive),
                     ('min_samples_split', exportFieldMethod.primitive),
                     ('subsample', exportFieldMethod.primitive),
                     ('min_samples_leaf', exportFieldMethod.primitive),
                     ('min_weight_fraction_leaf', exportFieldMethod.primitive),
                     ('max_leaf_nodes', exportFieldMethod.primitive),
                     ('min_impurity_decrease', exportFieldMethod.primitive),
                     ('presort', exportFieldMethod.primitive)])
        return fields

    def probabilistModel(self):
        return True

    def semiSupervisedModel(self):
        return False

    def featureImportance(self):
        return 'score'

    @staticmethod
    def generateParser(parser):
        ClassifierConf.generateParser(parser)
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


ClassifierConfFactory.getFactory().registerClass('GradientBoostingConf',
                                                 GradientBoostingConf)
