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

from . import ActiveLearningConfFactory
from .ActiveLearningConfiguration import ActiveLearningConfiguration

from SecuML.core.ActiveLearning.QueryStrategies.CesaBianchi import CesaBianchi
from SecuML.core.Classification.Configuration import ClassifierConfFactory
from SecuML.core.Classification.Configuration.TestConfiguration.ValidationDatasetConf import ValidationDatasetConf


class CesaBianchiConfiguration(ActiveLearningConfiguration):

    def __init__(self, auto, budget, batch, b, binary_model_conf, validation_conf, logger=None):
        ActiveLearningConfiguration.__init__(
            self, auto, budget, validation_conf, logger=logger)
        self.query_strategy = 'CesaBianchi'
        self.b = b
        self.batch = batch
        self.setBinaryModelConf(binary_model_conf)

    def setBinaryModelConf(self, binary_model_conf):
        conf = {}
        conf['binary'] = binary_model_conf
        ActiveLearningConfiguration.setModelsConf(self, conf)

    def getStrategy(self, iteration):
        return CesaBianchi(iteration)

    def generateSuffix(self):
        suffix = ''
        suffix += '__' + str(self.b)
        suffix += '__' + str(self.batch)
        return suffix

    @staticmethod
    def fromJson(obj):
        validation_conf = None
        if obj['validation_conf'] is not None:
            validation_conf = ValidationDatasetConf.fromJson(
                obj['validation_conf'])
        binary_model_conf = ClassifierConfFactory.getFactory(
        ).fromJson(obj['models_conf']['binary'])
        conf = CesaBianchiConfiguration(obj['auto'], obj['budget'],
                                        obj['batch'], obj['b'],
                                        binary_model_conf,
                                        validation_conf)
        return conf

    def toJson(self):
        conf = ActiveLearningConfiguration.toJson(self)
        conf['__type__'] = 'CesaBianchiConfiguration'
        conf['b'] = self.b
        conf['batch'] = self.batch
        return conf

    @staticmethod
    def generateParser(parser):
        al_group = ActiveLearningConfiguration.generateParser(parser)
        al_group.add_argument('--batch',
                              type=int,
                              default=100,
                              help='Number of annotations asked from the user at each iteration.')
        al_group.add_argument('--b',
                              type=float,
                              default=0.1)

    @staticmethod
    def generateParamsFromArgs(args):
        params = ActiveLearningConfiguration.generateParamsFromArgs(args)
        params['batch'] = args.batch
        params['b'] = args.b
        return params


ActiveLearningConfFactory.getFactory().registerClass('CesaBianchiConfiguration',
                                                     CesaBianchiConfiguration)
