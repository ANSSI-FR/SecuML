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

from SecuML.core.Classification.Configuration import ClassifierConfFactory
from SecuML.core.Classification.Configuration.TestConfiguration import TestConfiguration
from SecuML.core.Configuration import Configuration


class InvalidInputArguments(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ActiveLearningConfiguration(Configuration):

    def __init__(self, auto, budget, validation_conf, logger=None):
        Configuration.__init__(self, logger=logger)
        self.auto = auto
        self.budget = budget
        self.validation_conf = validation_conf

    @abc.abstractmethod
    def getStrategy(self, iteration):
        return

    @abc.abstractmethod
    def generateSuffix(self):
        return

    @staticmethod
    def fromJson(obj):
        return

    def toJson(self):
        conf = {}
        conf['__type__'] = 'ActiveLearningConfiguration'
        conf['auto'] = self.auto
        conf['budget'] = self.budget
        conf['models_conf'] = {}
        for key, model_conf in self.models_conf.items():
            conf['models_conf'][key] = model_conf.toJson()
        if self.validation_conf is not None:
            conf['validation_conf'] = self.validation_conf.toJson()
        else:
            conf['validation_conf'] = None
        return conf

    def setModelsConf(self, models_conf):
        self.models_conf = models_conf

    @staticmethod
    def generateSupervisedLearningArguments(parser, binary=True):
        supervised_group = parser.add_argument_group(
            'Supervised learning parameters')
        choices = ['LogisticRegression', 'Svc', 'GaussianNaiveBayes']
        if binary:
            choices += ['Sssvdd']
        supervised_group.add_argument('--model-class',
                                      choices=choices,
                                      default='LogisticRegression')
        supervised_group.add_argument('--num-folds',
                                      type=int,
                                      default=4)
        sample_weight_help = 'When set to True, the detection model is learned with '
        sample_weight_help += 'sample weights inverse to the proportion of the family '
        sample_weight_help += 'in the dataset. Useless if the families are not specified.'
        supervised_group.add_argument('--sample-weight',
                                      action='store_true',
                                      default=False,
                                      help=sample_weight_help)

    @staticmethod
    def generateActiveLearningArguments(parser):
        al_group = parser.add_argument_group(
            'Active learning parameters')
        al_group.add_argument('--init-annotations-file',
                              default='init_annotations.csv',
                              help='CSV file containing the initial annotations used to learn the first ' +
                              'supervised detection model.')
        auto_help = 'When set to True, the annotation queries are answered automatically by an oracle '
        auto_help += 'with the ground-truth labels stored in ground_truth.csv. '
        auto_help += '\nOtherwise, the user must answer some annotation queries in the web interface '
        auto_help += 'at each iteration.'
        al_group.add_argument('--auto',
                              dest='auto',
                              action='store_true',
                              default=False,
                              help=auto_help)
        al_group.add_argument('--budget',
                              type=int,
                              default=2000,
                              help='Total number of annotations asked from the user during the labeling procedure.')
        al_group.add_argument('--validation-dataset',
                              default=None,
                              help='The validation dataset must contain have ground-truth labels.')
        return al_group

    @staticmethod
    def generateParser(parser, classifier_conf=True, binary=True):
        al_group = ActiveLearningConfiguration.generateActiveLearningArguments(
            parser)
        if classifier_conf:
            ActiveLearningConfiguration.generateSupervisedLearningArguments(
                parser, binary=binary)
        return al_group

    @staticmethod
    def generateParamsFromArgs(args, binary_model_conf=None):
        if binary_model_conf is None:
            supervised_args = {}
            supervised_args['num_folds'] = args.num_folds
            supervised_args['sample_weight'] = args.sample_weight
            supervised_args['families_supervision'] = False
            test_conf = TestConfiguration()
            test_conf.setUnlabeled()
            supervised_args['test_conf'] = test_conf
            binary_model_conf = ClassifierConfFactory.getFactory().fromParam(
                args.model_class, supervised_args)

        active_learning_params = {}
        active_learning_params['auto'] = args.auto
        active_learning_params['budget'] = args.budget
        active_learning_params['binary_model_conf'] = binary_model_conf

        validation_conf = None
        if args.validation_dataset is not None:
            validation_conf = TestConfiguration()
            validation_conf.setTestDataset(args.validation_dataset)
        active_learning_params['validation_conf'] = validation_conf

        return active_learning_params
