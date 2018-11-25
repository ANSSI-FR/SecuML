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

from SecuML.core.Conf import Conf
from SecuML.core.Conf import exportFieldMethod

from .hyperparam_conf.HyperparamOptimConf import HyperparamOptimConf
from . import ClassifierConfFactory


class HyperParameter(object):

    def __init__(self, values):
        self.values = values
        self.best_value = None

    def setBestValue(self, best_value):
        self.best_value = best_value

    @staticmethod
    def from_json(obj):
        conf = HyperParameter(obj['values'])
        conf.setBestValue(obj['best_value'])
        return conf

    def to_json(self):
        conf = {}
        conf['__type__'] = 'HyperParameter'
        conf['values'] = self.values
        conf['best_value'] = self.best_value
        return conf


class ClassifierConf(Conf):

    def __init__(self, sample_weight, families_supervision,
                 hyperparams_optim_conf, logger):
        Conf.__init__(self, logger)
        self.sample_weight = sample_weight
        self.families_supervision = families_supervision
        self.model_class = None
        self.hyperparams_optim_conf = hyperparams_optim_conf
        self.probabilist_model = self.probabilistModel()
        self.semi_supervised = self.semiSupervisedModel()
        self.feature_importance = self.featureImportance()
        self.model_class_name = self.__class__.__name__.split('Conf')[0]

    def get_exp_name(self):
        name = self.model_class.__name__
        if self.families_supervision:
            name += '__FamiliesSupervision'
        return name

    @abc.abstractmethod
    def getParamGrid(self):
        return

    @abc.abstractmethod
    def setBestValues(self, grid_search):
        return

    @abc.abstractmethod
    def getBestValues(self):
        return

    def fieldsToExport(self):
        return [('sample_weight', exportFieldMethod.primitive),
                ('hyperparams_optim_conf', exportFieldMethod.obj),
                ('families_supervision', exportFieldMethod.primitive),
                ('probabilist_model', exportFieldMethod.primitive),
                ('feature_importance', exportFieldMethod.primitive),
                ('model_class_name', exportFieldMethod.primitive)]

    @staticmethod
    def hyperparamConfFromJson(obj, logger):
        if obj['hyperparams_optim_conf'] is None:
            return None
        return HyperparamOptimConf.from_json(obj['hyperparams_optim_conf'],
                                             logger)

    @staticmethod
    def hyperparamConfFromArgs(args, logger):
        return HyperparamOptimConf.fromArgs(args, logger)

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
    def generateCommonArguments(parser):
        return

    @staticmethod
    def generateParser(parser):
        ClassifierConf.generateCommonArguments(parser)
        HyperparamOptimConf.generateParser(parser)


ClassifierConfFactory.getFactory().registerClass('ClassifierConf',
                                                 ClassifierConf)
