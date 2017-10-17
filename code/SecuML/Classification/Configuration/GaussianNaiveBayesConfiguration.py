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

from SecuML.Classification.Classifiers.GaussianNaiveBayes import GaussianNaiveBayes
import ClassifierConfFactory
from ClassifierConfiguration import ClassifierConfiguration
from TestConfiguration import TestConfiguration

class GaussianNaiveBayesConfiguration(ClassifierConfiguration):

    def __init__(self, num_folds, sample_weight, families_supervision, test_conf):
        ClassifierConfiguration.__init__(self, num_folds, sample_weight,
                                         families_supervision, test_conf)
        if self.sample_weight:
            raise ValueError('Gaussian Naive Bayes does not support sample weights.')
        self.model_class = GaussianNaiveBayes

    def getModelClassName(self):
        return 'GaussianNaiveBayes'

    def getParamGrid(self):
        return None

    def setBestValues(self, grid_search):
        return

    def getBestValues(self):
        return None

    @staticmethod
    def fromJson(obj, exp):
        test_conf = TestConfiguration.fromJson(obj['test_conf'], exp)
        conf = GaussianNaiveBayesConfiguration(obj['num_folds'], obj['sample_weight'],
                                               obj['families_supervision'], test_conf)
        return conf

    def toJson(self):
        conf = ClassifierConfiguration.toJson(self)
        conf['__type__'] = 'GaussianNaiveBayesConfiguration'
        return conf

    def probabilistModel(self):
        return True

    def semiSupervisedModel(self):
        return False

    def featureImportance(self):
        return None

    @staticmethod
    def generateParser(parser):
        classifier_group = ClassifierConfiguration.generateParser(parser)

    @staticmethod
    def generateParamsFromArgs(args, experiment):
        params = ClassifierConfiguration.generateParamsFromArgs(args, experiment)
        return params

ClassifierConfFactory.getFactory().registerClass('GaussianNaiveBayesConfiguration',
        GaussianNaiveBayesConfiguration)
