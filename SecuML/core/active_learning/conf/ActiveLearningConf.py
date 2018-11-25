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

from SecuML.core.classification.conf import ClassifierConfFactory
from SecuML.core.classification.conf.ClassificationConf \
        import ClassificationConf
from SecuML.core.classification.conf.ClassifierConf import ClassifierConf
from SecuML.core.classification.conf.hyperparam_conf.HyperparamOptimConf \
        import HyperparamOptimConf
from SecuML.core.classification.conf.test_conf.UnlabeledLabeledConf \
                                import UnlabeledLabeledConf
from SecuML.core.classification.conf.test_conf.TestDatasetConf \
                                import TestDatasetConf
from SecuML.core.Conf import Conf
from SecuML.core.Conf import exportFieldMethod
from SecuML.core.tools.core_exceptions import SecuMLcoreException


class InvalidInputArguments(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ModelsConf(Conf):

    def __init__(self, models_conf):
        for k, conf in models_conf.items():
            self._add_conf(k, conf)

    def _add_conf(self, k, conf):
        setattr(self, k, conf)

    def items(self):
        return self.__dict__.items()

    def fieldsToExport(self):
        return [(k, exportFieldMethod.obj) for k in self.__dict__.keys()]

    @staticmethod
    def from_json(obj, logger):
        factory = ClassifierConfFactory.getFactory()
        models_conf = {}
        for k, model_obj in obj.items():
            models_conf[k] = factory.from_json(model_obj, logger)
        return ModelsConf(models_conf)


class ActiveLearningConf(Conf):

    def __init__(self, auto, budget, validation_conf, models_conf, logger):
        Conf.__init__(self, logger)
        self.auto = auto
        self.budget = budget
        self.validation_conf = validation_conf
        self.models_conf = ModelsConf(models_conf)

    @abc.abstractmethod
    def getStrategy(self, iteration):
        return

    def get_exp_name(self):
        return self.query_strategy

    @staticmethod
    def from_json(obj, logger):
        return

    def fieldsToExport(self):
        return [('auto', exportFieldMethod.primitive),
                ('budget', exportFieldMethod.primitive),
                ('validation_conf', exportFieldMethod.obj),
                ('models_conf', exportFieldMethod.obj)]

    @staticmethod
    def generateSupervisedLearningArguments(parser, binary=True):
        supervised_group = parser.add_argument_group(
                'Supervised learning parameters')
        choices = ['LogisticRegression', 'Svc', 'GaussianNaiveBayes']
        if binary:
            choices.extend(['Sssvdd'])
        supervised_group.add_argument('--model-class',
                                choices=choices,
                                default='LogisticRegression',
                                help='Model class trained at each iteration. '
                                     'Default: LogisticRegression.')
        HyperparamOptimConf.generateParser(supervised_group, subgroup=False)
        ClassifierConf.generateCommonArguments(supervised_group)

    @staticmethod
    def binaryModelConfFromArgs(args, logger):
        factory = ClassifierConfFactory.getFactory()
        classifier_conf = factory.fromArgs(args.model_class, args, logger)
        test_conf = UnlabeledLabeledConf(logger, None)
        return ClassificationConf(classifier_conf, test_conf, logger)

    @staticmethod
    def multiclassModelConfFromArgs(args, logger):
        factory = ClassifierConfFactory.getFactory()
        classifier_conf = factory.fromArgs(args.model_class, args, logger)
        classifier_conf.families_supervision = True
        test_conf = UnlabeledLabeledConf(logger, None)
        return ClassificationConf(classifier_conf, test_conf, logger)

    @staticmethod
    def generateActiveLearningArguments(parser):
        al_group = parser.add_argument_group('Active learning parameters')
        al_group.add_argument('--auto',
              dest='auto',
              action='store_true',
              default=False,
              help='When set to True, the annotation queries are answered '
                   'automatically by an oracle with the ground-truth labels '
                   'stored in ground_truth.csv. '
                   '\nOtherwise, the user must answer some annotation queries '
                   'in the web interface at each iteration.')
        al_group.add_argument('--budget',
              type=int,
              default=2000,
              help='Total number of annotations asked from the user during the '
                   'labeling procedure.')
        al_group.add_argument('--validation-dataset', default=None,
              help='The validation dataset.')
        return al_group

    @staticmethod
    def generateParser(parser, classifier_conf=False, binary=True):
        al_group = ActiveLearningConf.generateActiveLearningArguments(parser)
        if classifier_conf:
            ActiveLearningConf.generateSupervisedLearningArguments(parser,
                                                                  binary=binary)
        return al_group

    @staticmethod
    def validation_conf_from_args(args, logger):
        if args.validation_dataset is None:
            return None
        return TestDatasetConf(logger, None, args.validation_dataset)

    @staticmethod
    def validation_conf_from_json(conf_json, logger):
        if conf_json['validation_conf'] is None:
            return None
        return TestDatasetConf(logger, None, conf_json['validation_conf'])
