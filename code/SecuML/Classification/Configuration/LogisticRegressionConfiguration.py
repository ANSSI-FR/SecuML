## SecuML
## Copyright (C) 2016-2017  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

import numpy as np

from SecuML.Classification.Classifiers.LogisticRegression import LogisticRegression

import ClassifierConfFactory
from ClassifierConfiguration import ClassifierConfiguration, LearningParameter
from TestConfiguration import TestConfiguration

class LogisticRegressionConfiguration(ClassifierConfiguration):

    def __init__(self, num_folds, sample_weight, families_supervision, optim_algo, test_conf):
        ClassifierConfiguration.__init__(self, num_folds, sample_weight, families_supervision,
                test_conf = test_conf)
        self.model_class = LogisticRegression
        if optim_algo is not None:
            self.optim_algo = optim_algo
        else:
            self.optim_algo = 'liblinear'
        self.c = LearningParameter(list(10. ** np.arange(-2, 2)))
        if self.optim_algo == 'sag':
            self.penalty = LearningParameter(['l2'])
        elif self.optim_algo == 'liblinear':
            self.penalty = LearningParameter(['l1', 'l2'])

    def getModelClassName(self):
        return 'LogisticRegression'

    def generateSuffix(self):
        suffix = ClassifierConfiguration.generateSuffix(self)
        suffix += '__' + self.optim_algo
        return suffix

    def setC(self, c_values):
        self.c = LearningParameter(c_values)

    def setPenalty(self, penalty_values):
        self.penalty = LearningParameter(penalty_values)

    def setOptimAlgo(self, optim_algo):
        self.optim_algo = optim_algo

    def getParamGrid(self):
        param_grid = {'model__C': self.c.values, 'model__penalty': self.penalty.values}
        return param_grid

    def setBestValues(self, grid_search):
        self.c.setBestValue(grid_search.best_params_['model__C'])
        self.penalty.setBestValue(grid_search.best_params_['model__penalty'])

    def getBestValues(self):
        best_values = {'model__C': self.c.best_value,
                       'model__penalty': self.penalty.best_value}
        return best_values

    @staticmethod
    def fromJson(obj, exp):
        test_conf = TestConfiguration.fromJson(obj['test_conf'], exp)
        conf = LogisticRegressionConfiguration(obj['num_folds'], obj['sample_weight'],
                                               obj['families_supervision'], obj['optim_algo'],
                                               test_conf)
        conf.c          = LearningParameter.fromJson(obj['c'])
        conf.penalty    = LearningParameter.fromJson(obj['penalty'])
        conf.optim_algo = obj['optim_algo']
        return conf

    def toJson(self):
        conf = ClassifierConfiguration.toJson(self)
        conf['__type__']   = 'LogisticRegressionConfiguration'
        conf['optim_algo'] = self.optim_algo
        conf['c']          = self.c.toJson()
        conf['penalty']    = self.penalty.toJson()
        return conf

    def probabilistModel(self):
        return True

    def semiSupervisedModel(self):
        return False

    def featureCoefficients(self):
        return not(self.families_supervision)

    @staticmethod
    def generateParser(parser):
        ClassifierConfiguration.generateParser(parser)
        parser.add_argument('--optim-algo',
                choices = ['sag', 'liblinear'],
                default = 'liblinear',
                help = 'sag is recommended for large datasets.')

    @staticmethod
    def generateParamsFromArgs(args, experiment):
        params = ClassifierConfiguration.generateParamsFromArgs(args, experiment)
        params['optim_algo'] = args.optim_algo
        return params

ClassifierConfFactory.getFactory().registerClass('LogisticRegressionConfiguration',
        LogisticRegressionConfiguration)
