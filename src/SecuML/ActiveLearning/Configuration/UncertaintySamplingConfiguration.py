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

import ActiveLearningConfFactory
from ActiveLearningConfiguration import ActiveLearningConfiguration
from SecuML.ActiveLearning.QueryStrategies.UncertaintySampling import UncertaintySampling
from SecuML.ActiveLearning.QueryStrategies.UncertaintySamplingExp import UncertaintySamplingExp
from SecuML.Classification.Configuration import ClassifierConfFactory
from SecuML.Classification.Configuration.TestConfiguration import TestConfiguration

class UncertaintySamplingConfiguration(ActiveLearningConfiguration):

    def __init__(self, auto, budget, batch, binary_model_conf, validation_conf):
        ActiveLearningConfiguration.__init__(self, auto, budget, validation_conf)
        self.labeling_method = 'UncertaintySampling'
        self.batch           = batch
        self.setBinaryModelConf(binary_model_conf)

    def setBinaryModelConf(self, binary_model_conf):
        conf = {}
        conf['binary'] = binary_model_conf
        ActiveLearningConfiguration.setModelsConf(self, conf)

    def getStrategy(self, iteration):
        return UncertaintySampling(iteration)

    def getStrategyExp(self, iteration):
        return UncertaintySamplingExp(iteration)

    def generateSuffix(self):
        suffix  = ''
        suffix += '__' + str(self.batch)
        return suffix

    @staticmethod
    def fromJson(obj, experiment):
        validation_conf = None
        if obj['validation_conf'] is not None:
            validation_conf = TestConfiguration.fromJson(obj['validation_conf'],
                                                         experiment)
        binary_model_conf = ClassifierConfFactory.getFactory().fromJson(obj['models_conf']['binary'], experiment)
        conf = UncertaintySamplingConfiguration(obj['auto'], obj['budget'],
                                                obj['batch'], binary_model_conf,
                                                validation_conf)
        return conf

    def toJson(self):
        conf = ActiveLearningConfiguration.toJson(self)
        conf['__type__'] = 'UncertaintySamplingConfiguration'
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
    def generateParamsFromArgs(args, experiment):
        params = ActiveLearningConfiguration.generateParamsFromArgs(args, experiment)
        params['batch'] = args.batch
        return params

ActiveLearningConfFactory.getFactory().registerClass('UncertaintySamplingConfiguration',
        UncertaintySamplingConfiguration)
