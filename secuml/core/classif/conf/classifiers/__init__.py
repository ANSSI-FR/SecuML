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
from enum import Enum

from secuml.core.classif.conf.hyperparam import HyperparamConf
from secuml.core.conf import Conf
from secuml.core.conf import ConfFactory
from secuml.core.conf import exportFieldMethod


classifier_conf_factory = None


def get_factory():
    global classifier_conf_factory
    if classifier_conf_factory is None:
        classifier_conf_factory = ClassifierConfFactory()
    return classifier_conf_factory


class ClassifierType(Enum):
    unsupervised = 1
    semisupervised = 2
    supervised = 3


def get_classifier_type(class_):
    if issubclass(class_, UnsupervisedClassifierConf):
        return ClassifierType.unsupervised
    elif issubclass(class_, SemiSupervisedClassifierConf):
        return ClassifierType.semisupervised
    elif issubclass(class_, SupervisedClassifierConf):
        return ClassifierType.supervised
    elif issubclass(class_, ClassifierConf):
        return None
    raise ValueError('%s is not a classifier configuration.' % class_.__name__)


class ClassifierConfFactory(ConfFactory):

    def from_args(self, method, args, logger):
        class_ = self.methods[method + 'Conf']
        hyper_conf = None
        if method != 'AlreadyTrained':
            is_supervised = get_classifier_type(class_) == \
                                            ClassifierType.supervised
            hyper_conf = HyperparamConf.from_args(args, class_, is_supervised,
                                                  logger)
        return class_.from_args(args, hyper_conf, logger)

    def from_json(self, obj, logger):
        class_ = self.methods[obj['__type__']]
        hyper_conf = HyperparamConf.from_json(obj['hyperparam_conf'], class_,
                                              logger)
        return class_.from_json(obj['multiclass'], hyper_conf, obj, logger)

    def get_methods(self, classifier_type=None):
        all_classifiers = ConfFactory.get_methods(self)
        if classifier_type is None:
            return all_classifiers
        else:
            return [c for c in all_classifiers if
                    get_classifier_type(self.get_class(c)) == classifier_type]

    @staticmethod
    def get_default(model_class, num_folds, n_jobs, multiclass, logger):
        class_ = get_factory().get_class(model_class)
        hyper_conf = HyperparamConf.get_default(num_folds, n_jobs, multiclass,
                                                class_, logger)
        return class_(multiclass, hyper_conf, logger)


class ClassifierConf(Conf):

    def __init__(self, multiclass, hyperparam_conf, logger):
        Conf.__init__(self, logger)
        self.multiclass = multiclass
        self.model_class = None
        self.hyperparam_conf = hyperparam_conf
        self._set_characteristics()

    def get_exp_name(self):
        name = self.model_class_name
        if self.multiclass:
            name += '__Multiclass'
        return name

    def _set_characteristics(self):
        self.probabilist = self.is_probabilist()
        self.feature_importance = self.get_feature_importance()
        self._set_model_class()

    @abc.abstractmethod
    def _get_model_class(self):
        return

    def _set_model_class(self):
        self.model_class = self._get_model_class()
        self.model_class_name = self.model_class.__name__

    def fields_to_export(self):
        return [('hyperparam_conf', exportFieldMethod.obj),
                ('multiclass', exportFieldMethod.primitive),
                ('probabilist', exportFieldMethod.primitive),
                ('feature_importance', exportFieldMethod.primitive),
                ('model_class_name', exportFieldMethod.primitive)]

    @abc.abstractmethod
    def is_probabilist(self):
        return

    @abc.abstractmethod
    def scoring_function(self):
        return

    @abc.abstractmethod
    def get_feature_importance(self):
        return

    def is_interpretable(self):
        return self.get_feature_importance() in ['score', 'weight']

    def interpretable_predictions(self):
        return self.get_feature_importance() == 'weight'

    def get_coefs(self, model):
        feature_importance = self.get_feature_importance()
        if feature_importance == 'weight':
            return model.coef_[0]
        elif feature_importance == 'score':
            return model.feature_importances_
        else:
            return None


class SupervisedClassifierConf(ClassifierConf):

    def __init__(self, multiclass, hyperparam_conf, logger):
        ClassifierConf.__init__(self, multiclass, hyperparam_conf, logger)

    @staticmethod
    def gen_parser(parser, model_class):
        parser.add_argument('--multiclass', default=False, action='store_true')
        HyperparamConf.gen_parser(parser, model_class, True)


class UnsupervisedClassifierConf(ClassifierConf):

    def __init__(self, hyperparam_conf, logger):
        ClassifierConf.__init__(self, False, hyperparam_conf, logger)

    # TODO scikit-learn Pipeline does not support 'score_samples' yet.
    # scikit-learn issue #12542
    def scoring_function(self):
        # return 'score_samples'
        return None

    @staticmethod
    def gen_parser(parser, model_class):
        HyperparamConf.gen_parser(parser, model_class, False)


class SemiSupervisedClassifierConf(ClassifierConf):

    def __init__(self, multiclass, hyperparam_conf, logger):
        ClassifierConf.__init__(self, multiclass, hyperparam_conf, logger)

    @staticmethod
    def gen_parser(parser, model_class):
        parser.add_argument('--multiclass', default=False, action='store_true')
        HyperparamConf.gen_parser(parser, model_class, False)
