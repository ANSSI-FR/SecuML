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

from . import ActiveLearningConfFactory
from .ActiveLearningConfiguration import ActiveLearningConfiguration

from SecuML.core.ActiveLearning.QueryStrategies.Aladin import Aladin
from SecuML.core.Classification.Configuration import ClassifierConfFactory
from SecuML.core.Classification.Configuration.TestConfiguration.UnlabeledLabeledConf import UnlabeledLabeledConf
from SecuML.core.Classification.Configuration.TestConfiguration.ValidationDatasetConf import ValidationDatasetConf


def aladinMulticlassModelConf(logger):
    classifier_args = {}
    classifier_args['num_folds'] = 4
    classifier_args['sample_weight'] = False
    classifier_args['families_supervision'] = True
    classifier_args['alerts_conf'] = None
    classifier_args['optim_algo'] = 'liblinear'
    test_conf = UnlabeledLabeledConf()
    classifier_args['test_conf'] = test_conf
    factory = ClassifierConfFactory.getFactory()
    multiclass_model_conf = factory.fromParam('LogisticRegression',
                                              classifier_args,
                                              logger=logger)
    return multiclass_model_conf


class AladinConfiguration(ActiveLearningConfiguration):

    def __init__(self, auto, budget, num_annotations, binary_model_conf, validation_conf, logger=None):
        ActiveLearningConfiguration.__init__(
            self, auto, budget, validation_conf, logger=logger)
        self.query_strategy = 'Aladin'
        self.num_annotations = num_annotations
        self.setModelsConf(binary_model_conf)

    def setModelsConf(self, binary_model_conf):
        conf = {}
        conf['binary'] = binary_model_conf
        conf['multiclass'] = aladinMulticlassModelConf(self.logger)
        ActiveLearningConfiguration.setModelsConf(self, conf)

    def getStrategy(self, iteration):
        return Aladin(iteration)

    def generateSuffix(self):
        suffix = ''
        suffix += '__' + str(self.num_annotations)
        return suffix

    @staticmethod
    def fromJson(obj):
        validation_conf = None
        if obj['validation_conf'] is not None:
            validation_conf = ValidationDatasetConf.fromJson(
                obj['validation_conf'])
        binary_model_conf = ClassifierConfFactory.getFactory().fromJson(
            obj['models_conf']['binary'])
        conf = AladinConfiguration(obj['auto'], obj['budget'],
                                   obj['num_annotations'], binary_model_conf, validation_conf)
        return conf

    def toJson(self):
        conf = ActiveLearningConfiguration.toJson(self)
        conf['__type__'] = 'AladinConfiguration'
        conf['num_annotations'] = self.num_annotations
        return conf

    @staticmethod
    def generateParser(parser):
        al_group = ActiveLearningConfiguration.generateParser(parser,
                                                              classifier_conf=False)
        al_group.add_argument('--num-annotations',
                              type=int,
                              default=100,
                              help='Number of annotations asked from the user at each iteration.')

    @staticmethod
    def generateParamsFromArgs(args):
        supervised_args = {}
        supervised_args['num_folds'] = 4
        supervised_args['sample_weight'] = False
        supervised_args['families_supervision'] = False
        test_conf = UnlabeledLabeledConf()
        supervised_args['test_conf'] = test_conf
        binary_model_conf = ClassifierConfFactory.getFactory().fromParam(
            'LogisticRegression', supervised_args)
        params = ActiveLearningConfiguration.generateParamsFromArgs(args,
                                                                    binary_model_conf=binary_model_conf)
        params['num_annotations'] = args.num_annotations
        return params


ActiveLearningConfFactory.getFactory().registerClass('AladinConfiguration',
                                                     AladinConfiguration)
