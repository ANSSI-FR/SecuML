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

from SecuML.core.classification.classifiers.Svc import Svc
from SecuML.core.Conf import exportFieldMethod

from . import ClassifierConfFactory
from .ClassifierConf import ClassifierConf, HyperParameter


class SvcConf(ClassifierConf):

    def __init__(self, sample_weight, families_supervision,
                 hyperparams_optim_conf, logger):
        ClassifierConf.__init__(self, sample_weight,
                                families_supervision,
                                hyperparams_optim_conf,
                                logger)
        self.model_class = Svc
        self.c = HyperParameter(list(10. ** np.arange(-2, 2)))

    def setC(self, c_values):
        self.c = HyperParameter(c_values)

    def getParamGrid(self):
        param_grid = {'model__C': self.c.values}
        return param_grid

    def setBestValues(self, grid_search):
        self.c.setBestValue(grid_search.best_params_['model__C'])

    def getBestValues(self):
        best_values = {'model__C': self.c.best_value}
        return best_values

    def fieldsToExport(self):
        fields = ClassifierConf.fieldsToExport(self)
        fields.extend([('c', exportFieldMethod.obj)])
        return fields

    def probabilistModel(self):
        return False

    def semiSupervisedModel(self):
        return False

    def featureImportance(self):
        return None

    @staticmethod
    def generateParser(parser):
        ClassifierConf.generateParser(parser)

    @staticmethod
    def from_json(obj, logger):
        hyper_conf = ClassifierConf.hyperparamConfFromJson(obj, logger)
        conf = SvcConf(obj['sample_weight'],
                       obj['families_supervision'],
                       hyper_conf,
                       logger)
        conf.c = HyperParameter.from_json(obj['c'])
        return conf

    @staticmethod
    def fromArgs(args, logger):
        hyper_conf = ClassifierConf.hyperparamConfFromArgs(args, logger)
        return SvcConf(False,
                       None,
                       hyper_conf,
                       logger)


ClassifierConfFactory.getFactory().registerClass('SvcConf', SvcConf)
