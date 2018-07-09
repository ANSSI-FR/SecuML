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

import abc

from SecuML.core.Configuration import Configuration
from SecuML.core.Classification.Configuration.TestConfiguration \
        import TestConfFactory
from SecuML.core.Tools import date_tools

from . import ClassifierConfFactory


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

    def __init__(self, num_folds, sample_weight, families_supervision,
                 test_conf, logger=None):
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
    def generateAlertParser(parser):
        alerts_group = parser.add_argument_group(
            'Alerts parameters. Useful only when validation_dataset is set to random_split or validation.')
        alerts_group.add_argument('--detection-threshold',
                                  type=float,
                                  default=0.8,
                                  help='An alert is raised if the predicted probability of maliciousness ' +
                                  'is above this threshold. ' +
                                  'Default: 0.8.')
        alerts_group.add_argument('--top-n-alerts',
                                  default=100,
                                  type=int,
                                  help='Number of most confident alerts displayed.')
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
    def generateValidationParser(parser):
        validation_group = parser.add_argument_group('Validation parameters')
        type_help = 'Default: RandomSplit. '
        type_help += 'TemporalSplit, CutoffTime, TemporalCv, and '
        type_help += 'SlidingWindow require timestamped instances. '
        validation_group.add_argument('--validation-mode',
                                      choices=['RandomSplit',
                                               'TemporalSplit',
                                               'CutoffTime',
                                               'Cv',
                                               'TemporalCv',
                                               'SlidingWindow',
                                               'ValidationDataset'],
                                      default='RandomSplit',
                                      help=type_help)
        # random_split or temporal_split
        split_help = 'Useful only when validation-type is set to RandomSplit or to TemporalSplit. '
        split_help += 'Specify the pourcentage of the training data selected for validation. '
        split_help += 'Default: 0.1'
        validation_group.add_argument('--test-size',
                                      type=float,
                                      default=0.1,
                                      help=split_help)

        # cutoff_time
        cutoff_time_help = 'Useful only when validation-type is set to CutoffTime. '
        cutoff_time_help += 'Specify the cutoff time. Format: YYYY-MM-DD HH:MM:SS. '
        validation_group.add_argument('--cutoff-time',
                                      type=date_tools.valid_date,
                                      help=cutoff_time_help)

        # cv or temporal_cv
        cv_help = 'Useful only when validation-type is set to Cv or to TemporalCv. '
        cv_help += 'Specify the number of folds built in the cross validation. '
        cv_help += 'Default: 4.'
        validation_group.add_argument('--num-validation-folds',
                                      type=int,
                                      default=4,
                                      help=cv_help)
        # sliding_window
        num_buckets_help = 'Useful only when validation-type is set to SlidingWindow. '
        num_buckets_help += 'Specify the number of buckets. '
        num_buckets_help += 'Default: 10.'
        validation_group.add_argument('--num-buckets',
                                      type=int,
                                      default=10,
                                      help=num_buckets_help)
        num_train_buckets_help = 'Useful only when validation-type is set to SlidingWindow. '
        num_train_buckets_help += 'Specify the number of train buckets. '
        num_train_buckets_help += 'Default: 4.'
        validation_group.add_argument('--num-train-buckets',
                                      type=int,
                                      default=4,
                                      help=num_train_buckets_help)
        num_test_buckets_help = 'Useful only when validation-type is set to SlidingWindow. '
        num_test_buckets_help += 'Specify the number of test buckets. '
        num_test_buckets_help += 'Default: 1.'
        validation_group.add_argument('--num-test-buckets',
                                      type=int,
                                      default=1,
                                      help=num_test_buckets_help)

        # dataset
        dataset_help = 'Useful only when validation-type is set to ValidationDataset. '
        dataset_help += 'Specify the name of the validation dataset.'
        validation_group.add_argument('--validation-dataset',
                                      default=None,
                                      help=dataset_help)

    @staticmethod
    def generateParser(parser):
        num_folds_help = 'Number of folds built in the cross validation looking for the best hyper-parameters. '
        num_folds_help += 'Default: 4.'
        parser.add_argument('--num-folds',
                            type=int,
                            default=4,
                            help=num_folds_help)
        sample_weight_help = 'When set to True, the detection model is learned with '
        sample_weight_help += 'sample weights inverse to the proportion of the family '
        sample_weight_help += 'in the dataset. Useless if the families are not specified in '
        sample_weight_help += 'the ground-truth labels.'
        parser.add_argument('--sample-weight',
                            action='store_true',
                            default=False,
                            help=sample_weight_help)

        ClassifierConfiguration.generateValidationParser(parser)
        ClassifierConfiguration.generateAlertParser(parser)

    @staticmethod
    def generateParamsFromArgs(args):
        params = {}
        params['num_folds'] = args.num_folds
        params['sample_weight'] = args.sample_weight
        params['families_supervision'] = False
        factory = TestConfFactory.getFactory()
        params['test_conf'] = factory.fromArgs(args.validation_mode, args)
        return params


ClassifierConfFactory.getFactory().registerClass('ClassifierConfiguration',
                                                 ClassifierConfiguration)
