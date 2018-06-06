# SecuML
# Copyright (C) 2016-2017  ANSSI
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

import abc

from SecuML.core.Clustering.Configuration import ClusteringConfFactory
from SecuML.core.Configuration import Configuration

from . import ClassifierConfFactory
from .AlertsConfiguration import AlertsConfiguration
from .TestConfiguration import TestConfiguration


class LearningParameter(object):

    def __init__(self, values):
        self.values = values
        self.best_value = None

    def setBestValue(self, best_value):
        self.best_value = best_value

    @staticmethod
    def fromJson(obj):
        conf = LearningParameter(obj['values'])
        conf.setBestValue(obj['best_value'])
        return conf

    def toJson(self):
        conf = {}
        conf['__type__'] = 'LearningParameter'
        conf['values'] = self.values
        conf['best_value'] = self.best_value
        return conf


class ClassifierConfiguration(Configuration):

    def __init__(self, num_folds, sample_weight, families_supervision, test_conf, logger=None):
        Configuration.__init__(self, logger=logger)
        self.num_folds = num_folds
        self.sample_weight = sample_weight
        self.families_supervision = families_supervision
        self.model_class = None
        self.test_conf = test_conf
        self.probabilist_model = self.probabilistModel()
        self.semi_supervised = self.semiSupervisedModel()
        self.feature_importance = self.featureImportance()

    def generateSuffix(self):
        suffix = '__' + self.getModelClassName()
        if self.sample_weight:
            suffix += '__' + 'SampleWeight'
        if self.families_supervision:
            suffix += '__' + 'FamiliesSupervision'
        suffix += self.test_conf.generateSuffix()
        return suffix

    @abc.abstractmethod
    def getModelClassName(self):
        return

    @abc.abstractmethod
    def getParamGrid(self):
        return

    @abc.abstractmethod
    def setBestValues(self, grid_search):
        return

    @abc.abstractmethod
    def getBestValues(self):
        return

    def toJson(self):
        conf = {}
        conf['__type__'] = 'ClassifierConfiguration'
        conf['model_class'] = self.model_class.__name__
        conf['num_folds'] = self.num_folds
        conf['sample_weight'] = self.sample_weight
        conf['test_conf'] = self.test_conf.toJson()
        conf['families_supervision'] = self.families_supervision
        conf['probabilist_model'] = self.probabilist_model
        conf['feature_importance'] = self.feature_importance
        return conf

    @abc.abstractmethod
    def probabilistModel(self):
        return

    @abc.abstractmethod
    def semiSupervisedModel(self):
        return

    @abc.abstractmethod
    def featureImportance(self):
        return

    @staticmethod
    def generateParser(parser):
        num_folds_help = 'Number of folds built in the cross validation looking for the best hyper parameters. '
        num_folds_help += 'Default: 4.'
        parser.add_argument('--num-folds',
                            type=int,
                            default=4,
                            help=num_folds_help)
        parser.add_argument('--multilabel',
                            action='store_true',
                            default=False)
        sample_weight_help = 'When set to True, the detection model is learned with '
        sample_weight_help += 'sample weights inverse to the proportion of the family '
        sample_weight_help += 'in the dataset. Useless if the families are not specified in '
        sample_weight_help += 'the ground-truth labels.'
        parser.add_argument('--sample-weight',
                            action='store_true',
                            default=False,
                            help=sample_weight_help)

        # Validation parameters
        validation_group = parser.add_argument_group('Validation parameters')
        type_help = 'random_split (default value): test-size pourcent of the training data are selected randomy for validation.'
        type_help += 'cv: cross validation performed with num-folds folds.'
        type_help += 'validated: a separate dataset, validation-dataset, is used for validation'
        validation_group.add_argument('--validation-type',
                                      choices=['random_split',
                                               'cv', 'dataset'],
                                      default='random_split',
                                      help='Default: random_split')
        # random_split
        random_split_help = 'Useful only when validation-type is set to random_split. '
        random_split_help += 'Specify the pourcentage of the training data selected for validation. '
        random_split_help += 'Default: 0.1'
        validation_group.add_argument('--test-size',
                                      type=float,
                                      default=0.1,
                                      help=random_split_help)
        # cv
        cv_help = 'Useful only when validation-type is set to cv. '
        cv_help += 'Specify the number of folds built in the validation cross validation. '
        cv_help += 'Default: 4.'
        validation_group.add_argument('--num-validation-folds',
                                      type=int,
                                      default=4,
                                      help=cv_help)
        # dataset
        dataset_help = 'Useful only when validation-type is set to dataset. '
        dataset_help += 'Specify the name of the validation dataset.'
        validation_group.add_argument('--validation-dataset',
                                      default=None,
                                      help=dataset_help)

        # Alerts
        alerts_group = parser.add_argument_group(
            'Alerts parameters. Useful only when validation_dataset is set to random_split or validation.')
        alerts_group.add_argument('--top-n-alerts',
                                  default=100,
                                  type=int,
                                  help='Number of most confident alerts displayed.')
        alerts_group.add_argument('--detection-threshold',
                                  type=float,
                                  default=0.8,
                                  help='An alert is raised if the predicted probability of maliciousness ' +
                                  'is above this threshold. ' +
                                  'Default: 0.8.')
        alerts_group.add_argument('--clustering-algo',
                                  default='Kmeans',
                                  choices=['Kmeans', 'GaussianMixture'],
                                  help='Clustering algorithm to analyse the alerts. ' +
                                  'Default: Kmeans.')
        alerts_group.add_argument('--num-clusters',
                                  type=int,
                                  default=4,
                                  help='Number of clusters built from the alerts. ' +
                                  'Default: 4.')

    @staticmethod
    def generateParamsFromArgs(args):
        # Alerts configuration
        alerts_conf = None
        # The alerts are not analyzed in CV mode
        if args.validation_type != 'cv':
            params = {}
            params['num_clusters'] = args.num_clusters
            params['num_results'] = None
            params['projection_conf'] = None
            params['label'] = 'all'
            clustering_conf = ClusteringConfFactory.getFactory().fromParam(
                args.clustering_algo,
                params)
            alerts_conf = AlertsConfiguration(args.top_n_alerts, args.detection_threshold,
                                              clustering_conf)

        # Test configuration
        test_conf = TestConfiguration(alerts_conf=alerts_conf)
        if args.validation_type == 'dataset':
            test_conf.setTestDataset(args.validation_dataset)
        elif args.validation_type == 'random_split':
            test_conf.setRandomSplit(args.test_size)
        elif args.validation_type == 'cv':
            test_conf.setCvNumFolds(args.num_validation_folds)

        params = {}
        params['num_folds'] = args.num_folds
        params['sample_weight'] = args.sample_weight
        params['families_supervision'] = args.multilabel
        params['test_conf'] = test_conf

        return params


ClassifierConfFactory.getFactory().registerClass('ClassifierConfiguration',
                                                 ClassifierConfiguration)
