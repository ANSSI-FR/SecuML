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

from SecuML.core.classification.classifiers.GaussianNaiveBayes \
        import GaussianNaiveBayes
from SecuML.core.tools.core_exceptions import SecuMLcoreException
from . import ClassifierConfFactory
from .ClassifierConf import ClassifierConf


class GaussianNaiveBayesConf(ClassifierConf):

    def __init__(self, sample_weight, families_supervision,
                 hyperparams_optim_conf, logger):
        ClassifierConf.__init__(self, sample_weight,
                                families_supervision,
                                hyperparams_optim_conf,
                                logger)
        if self.sample_weight:
            raise SecuMLcoreException('Gaussian Naive Bayes does not support '
                                      'sample weights.')
        self.model_class = GaussianNaiveBayes

    def getParamGrid(self):
        return None

    def setBestValues(self, grid_search):
        return

    def getBestValues(self):
        return None

    @staticmethod
    def from_json(obj, logger):
        hyper_conf = ClassifierConf.hyperparamConfFromJson(obj, logger)
        return GaussianNaiveBayesConf(obj['sample_weight'],
                                      obj['families_supervision'],
                                      hyper_conf, logger)

    def probabilistModel(self):
        return True

    def semiSupervisedModel(self):
        return False

    def featureImportance(self):
        return None

    @staticmethod
    def fromArgs(args, logger):
        hyper_conf = ClassifierConf.hyperparamConfFromArgs(args, logger)
        return GaussianNaiveBayesConf(False, None, hyper_conf,
                                      logger)


ClassifierConfFactory.getFactory().registerClass('GaussianNaiveBayesConf',
                                                  GaussianNaiveBayesConf)
