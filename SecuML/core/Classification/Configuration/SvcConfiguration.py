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

import numpy as np

from SecuML.core.Classification.Classifiers.Svc import Svc
from . import ClassifierConfFactory
from .ClassifierConfiguration import ClassifierConfiguration, LearningParameter
from .TestConfiguration import TestConfiguration


class SvcConfiguration(ClassifierConfiguration):

    def __init__(self, num_folds, sample_weight, families_supervision, test_conf,
                 logger=None):
        ClassifierConfiguration.__init__(self, num_folds, sample_weight,
                                         families_supervision, test_conf=test_conf,
                                         logger=logger)
        self.model_class = Svc
        self.c = LearningParameter(list(10. ** np.arange(-2, 2)))

    def getModelClassName(self):
        return 'Svc'

    def setC(self, c_values):
        self.c = LearningParameter(c_values)

    def getParamGrid(self):
        param_grid = {'model__C': self.c.values}
        return param_grid

    def setBestValues(self, grid_search):
        self.c.setBestValue(grid_search.best_params_['model__C'])

    def getBestValues(self):
        best_values = {'model__C': self.c.best_value}
        return best_values

    @staticmethod
    def fromJson(obj):
        test_conf = TestConfiguration.fromJson(obj['test_conf'])
        conf = SvcConfiguration(obj['num_folds'], obj['sample_weight'],
                                obj['families_supervision'], test_conf)
        conf.c = LearningParameter.fromJson(obj['c'])
        return conf

    def toJson(self):
        conf = ClassifierConfiguration.toJson(self)
        conf['__type__'] = 'SvcConfiguration'
        conf['c'] = self.c.toJson()
        return conf

    def probabilistModel(self):
        return False

    def semiSupervisedModel(self):
        return False

    def featureImportance(self):
        return None

    @staticmethod
    def generateParser(parser):
        ClassifierConfiguration.generateParser(parser)

    @staticmethod
    def generateParamsFromArgs(args):
        params = ClassifierConfiguration.generateParamsFromArgs(args)
        return params


ClassifierConfFactory.getFactory().registerClass(
    'SvcConfiguration', SvcConfiguration)
