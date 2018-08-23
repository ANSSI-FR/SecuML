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

from SecuML.core.Classification.Classifiers.Sssvdd import Sssvdd
from . import ClassifierConfFactory
from .ClassifierConfiguration import ClassifierConfiguration
from .TestConfiguration import TestConfFactory


class SssvddConfiguration(ClassifierConfiguration):

    def __init__(self, n_jobs, num_folds, test_conf, logger=None):
        ClassifierConfiguration.__init__(self, n_jobs, num_folds, False, False,
                                         test_conf, logger=logger)
        self.model_class = Sssvdd

    def getModelClassName(self):
        return 'Sssvdd'

    def getParamGrid(self):
        return None

    def setBestValues(self, grid_search):
        return

    def getBestValues(self):
        return None

    @staticmethod
    def fromJson(obj, logger=None):
        test_conf = TestConfFactory.getFactory().fromJson(obj['test_conf'],
                                                          logger=logger)
        conf = SssvddConfiguration(obj['n_jobs'], obj['num_folds'], test_conf,
                                   logger=logger)
        return conf

    def toJson(self):
        conf = ClassifierConfiguration.toJson(self)
        conf['__type__'] = 'SssvddConfiguration'
        return conf

    def probabilistModel(self):
        return False

    def semiSupervisedModel(self):
        return True

    def featureImportance(self):
        return None


ClassifierConfFactory.getFactory().registerClass('SssvddConfiguration',
                                                 SssvddConfiguration)
