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

import numpy as np

from SecuML.core.classification.classifiers.LogisticRegression \
        import LogisticRegression
from SecuML.core.Conf import exportFieldMethod

from . import ClassifierConfFactory
from .ClassifierConf import ClassifierConf, HyperParameter


class LogisticRegressionConf(ClassifierConf):

    def __init__(self, sample_weight, families_supervision, optim_algo,
                 hyperparams_optim_conf, logger):
        ClassifierConf.__init__(self, sample_weight, families_supervision,
                                hyperparams_optim_conf, logger)
        self.model_class = LogisticRegression
        if optim_algo is not None:
            self.optim_algo = optim_algo
        else:
            self.optim_algo = 'liblinear'
        self.c = HyperParameter(list(10. ** np.arange(-2, 2)))
        if self.optim_algo == 'sag':
            self.penalty = HyperParameter(['l2'])
        elif self.optim_algo == 'liblinear':
            self.penalty = HyperParameter(['l1', 'l2'])

    def get_exp_name(self):
        name = ClassifierConf.get_exp_name(self)
        name += '__%s' % self.optim_algo
        return name

    def setC(self, c_values):
        self.c = HyperParameter(c_values)

    def setPenalty(self, penalty_values):
        self.penalty = HyperParameter(penalty_values)

    def setOptimAlgo(self, optim_algo):
        self.optim_algo = optim_algo

    def getParamGrid(self):
        param_grid = {'model__C': self.c.values,
                      'model__penalty': self.penalty.values}
        return param_grid

    def setBestValues(self, grid_search):
        self.c.setBestValue(grid_search.best_params_['model__C'])
        self.penalty.setBestValue(grid_search.best_params_['model__penalty'])

    def getBestValues(self):
        return {'model__C': self.c.best_value,
                'model__penalty': self.penalty.best_value}

    def fieldsToExport(self):
        fields = ClassifierConf.fieldsToExport(self)
        fields.extend([('optim_algo', exportFieldMethod.primitive),
                       ('c', exportFieldMethod.obj),
                       ('penalty', exportFieldMethod.obj)])
        return fields

    def probabilistModel(self):
        return True

    def semiSupervisedModel(self):
        return False

    def featureImportance(self):
        if not self.families_supervision:
            return 'weight'
        else:
            return None

    @staticmethod
    def generateParser(parser):
        ClassifierConf.generateParser(parser)
        parser.add_argument('--optim-algo',
                            choices=['sag', 'liblinear'],
                            default='liblinear',
                            help='sag is recommended for large datasets.'
                                 'Default: liblinear.')

    @staticmethod
    def from_json(obj, logger):
        hyper_conf = ClassifierConf.hyperparamConfFromJson(obj, logger)
        conf = LogisticRegressionConf(obj['sample_weight'],
                                      obj['families_supervision'],
                                      obj['optim_algo'],
                                      hyper_conf,
                                      logger)
        conf.c = HyperParameter.from_json(obj['c'])
        conf.penalty = HyperParameter.from_json(obj['penalty'])
        return conf

    @staticmethod
    def fromArgs(args, logger):
        hyper_conf = ClassifierConf.hyperparamConfFromArgs(args, logger)
        optim_algo = 'liblinear'
        if hasattr(args, 'optim_algo'):
            optim_algo = args.optim_algo
        return LogisticRegressionConf(False, False, optim_algo,
                                      hyper_conf, logger)

ClassifierConfFactory.getFactory().registerClass('LogisticRegressionConf',
                                                 LogisticRegressionConf)
