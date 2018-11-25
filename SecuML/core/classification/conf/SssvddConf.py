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

from SecuML.core.classification.classifiers.Sssvdd import Sssvdd
from . import ClassifierConfFactory
from .ClassifierConf import ClassifierConf


class SssvddConf(ClassifierConf):

    def __init__(self, hyperparams_optim_conf, logger):
        ClassifierConf.__init__(self, False, False, hyperparams_optim_conf,
                                logger)
        self.model_class = Sssvdd

    def getParamGrid(self):
        return None

    def setBestValues(self, grid_search):
        return

    def getBestValues(self):
        return None

    @staticmethod
    def from_json(obj, logger):
        hyper_conf = ClassifierConf.hyperparamConfFromJson(obj, logger)
        return SssvddConf(hyper_conf, logger)

    @staticmethod
    def fromArgs(args, logger):
        hyper_conf = ClassifierConf.hyperparamConfFromArgs(args, logger)
        return SssvddConf(hyper_conf, logger)

    def probabilistModel(self):
        return False

    def semiSupervisedModel(self):
        return True

    def featureImportance(self):
        return None


ClassifierConfFactory.getFactory().registerClass('SssvddConf', SssvddConf)
