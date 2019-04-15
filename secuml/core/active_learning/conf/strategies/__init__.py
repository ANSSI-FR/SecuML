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

import abc

from secuml.core.classif.conf import classifiers
from secuml.core.classif.conf.classifiers import ClassifierType
from secuml.core.classif.conf import ClassificationConf
from secuml.core.classif.conf.hyperparam import HyperparamConf
from secuml.core.classif.conf.test.unlabeled_labeled \
        import UnlabeledLabeledConf
from secuml.core.classif.conf.test.test_dataset import TestDatasetConf
from secuml.core.conf import Conf
from secuml.core.conf import ConfFactory
from secuml.core.conf import exportFieldMethod


active_learning_conf_factory = None


def get_factory():
    global active_learning_conf_factory
    if active_learning_conf_factory is None:
        active_learning_conf_factory = ActiveLearningConfFactory()
    return active_learning_conf_factory


class ActiveLearningConfFactory(ConfFactory):

    def from_args(self, method, args, logger):
        validation_conf = None
        if args.validation_dataset is not None:
            validation_conf = TestDatasetConf(logger, args.validation_dataset)
        class_ = self.get_class(method)
        main_model_type = class_.main_model_type()
        main_model_conf = None
        if main_model_type is not None:
            factory = classifiers.get_factory()
            args.multiclass = main_model_type == 'multiclass'
            classifier_conf = factory.from_args(args.model_class, args, logger)
            test_conf = UnlabeledLabeledConf(logger)
            main_model_conf = ClassificationConf(
                                            classifier_conf, test_conf,
                                            logger,
                                            validation_conf=validation_conf)
        return class_.from_args(args, main_model_conf, validation_conf, logger)

    def from_json(self, obj, logger):
        class_name = obj['__type__']
        main_model = ClassificationConf.from_json(obj['main_model_conf'],
                                                  logger)
        validation_conf = None
        if obj['validation_conf'] is None:
            return None
        validation_conf = TestDatasetConf(logger, obj['validation_conf'])
        return self.methods[class_name].from_json(obj, main_model,
                                                  validation_conf, logger)


class ActiveLearningConf(Conf):

    def __init__(self, auto, budget, main_model_conf, validation_conf, logger):
        Conf.__init__(self, logger)
        self.auto = auto
        self.budget = budget
        self.main_model_conf = main_model_conf
        self.validation_conf = validation_conf
        self._set_strategy()

    def get_strategy(self, iteration):
        return self.strategy(iteration)

    def _set_strategy(self):
        self.strategy = self._get_strategy()
        self.strategy_name = self.strategy.__name__

    @abc.abstractmethod
    def _get_strategy(self):
        return

    def get_exp_name(self):
        return self.strategy_name

    def fields_to_export(self):
        return [('strategy_name', exportFieldMethod.primitive),
                ('auto', exportFieldMethod.primitive),
                ('budget', exportFieldMethod.primitive),
                ('main_model_conf', exportFieldMethod.obj),
                ('validation_conf', exportFieldMethod.obj)]

    @staticmethod
    def gen_main_model_parser(parser):
        group = parser.add_argument_group('Classification model parameters')
        factory = classifiers.get_factory()
        models = factory.get_methods(ClassifierType.supervised)
        group.add_argument('--model-class',
                           choices=models,
                           default='LogisticRegression',
                           help='Model class trained at each iteration. '
                                'Default: LogisticRegression.')
        HyperparamConf.gen_parser(group, None, True, subgroup=False)

    @staticmethod
    def gen_parser(parser, main_model=True):
        al_group = parser.add_argument_group('Active learning parameters')
        al_group.add_argument(
              '--auto',
              dest='auto',
              action='store_true',
              default=False,
              help='When specified, the annotation queries are answered '
                   'automatically by an oracle with the ground-truth labels '
                   'stored in ground_truth.csv. '
                   '\nOtherwise, the user must answer some annotation queries '
                   'in the web interface at each iteration.')
        al_group.add_argument(
              '--budget',
              type=int,
              default=2000,
              help='Total number of annotations asked from the user during '
                   'the labeling procedure.')
        al_group.add_argument('--validation-dataset', default=None,
                              help='The validation dataset.')
        if main_model:
            ActiveLearningConf.gen_main_model_parser(parser)
        return al_group
