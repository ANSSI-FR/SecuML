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

import ActiveLearningConfFactory
from ActiveLearningConfiguration import ActiveLearningConfiguration
from SecuML.ActiveLearning.QueryStrategies.RandomSampling import RandomSampling
from SecuML.Classification.Configuration import ClassifierConfFactory

class RandomSamplingConfiguration(ActiveLearningConfiguration):

    def __init__(self, auto, budget, batch, binary_model_conf):
        ActiveLearningConfiguration.__init__(self, auto, budget)
        self.labeling_method = 'RandomSampling'
        self.batch           = batch
        self.setBinaryModelConf(binary_model_conf)

    def setBinaryModelConf(self, binary_model_conf):
        conf = {}
        conf['binary'] = binary_model_conf
        ActiveLearningConfiguration.setModelsConf(self, conf)

    def getStrategy(self, iteration):
        return RandomSampling(iteration)

    def generateSuffix(self):
        suffix  = ''
        suffix += '__' + str(self.batch)
        return suffix

    @staticmethod
    def fromJson(obj, experiment):
        binary_model_conf = ClassifierConfFactory.getFactory().fromJson(
                obj['models_conf']['binary'], experiment)
        conf = RandomSamplingConfiguration(obj['auto'], obj['budget'], obj['batch'],
                                           binary_model_conf)
        return conf

    def toJson(self):
        conf = ActiveLearningConfiguration.toJson(self)
        conf['__type__'] = 'RandomSamplingConfiguration'
        conf['batch']    = self.batch
        return conf

    @staticmethod
    def generateParser(parser):
        al_group = ActiveLearningConfiguration.generateParser(parser)
        al_group.add_argument('--batch',
                type = int,
                default = 100,
                help = 'Number of annotations asked from the user at each iteration.')

    @staticmethod
    def generateParamsFromArgs(args):
        params = ActiveLearningConfiguration.generateParamsFromArgs(args)
        params['batch'] = args.batch
        return params

ActiveLearningConfFactory.getFactory().registerClass('RandomSamplingConfiguration',
        RandomSamplingConfiguration)
