## SecuML
## Copyright (C) 2016  ANSSI
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

from SecuML.Classification.Classifiers.Sssvdd import Sssvdd
import ClassifierConfFactory
from ClassifierConfiguration import ClassifierConfiguration

class SssvddConfiguration(ClassifierConfiguration):

    def __init__(self, num_folds, test_conf):
        ClassifierConfiguration.__init__(self, num_folds, False, False, test_conf)
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
    def fromJson(obj, exp):
        conf = SssvddConfiguration(obj['num_folds'])
        ClassifierConfiguration.setTestConfiguration(conf, obj, exp)
        return conf

    def toJson(self):
        conf = ClassifierConfiguration.toJson(self)
        conf['__type__'] = 'SssvddConfiguration'
        return conf

    def probabilistModel(self):
        return False

    def semiSupervisedModel(self):
        return True

    def featureCoefficients(self):
        return False

ClassifierConfFactory.getFactory().registerClass('SssvddConfiguration',
        SssvddConfiguration)
