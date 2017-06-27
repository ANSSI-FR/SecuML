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
from SecuML.ActiveLearning.QueryStrategies.Aladin import Aladin
from SecuML.Classification.Configuration import ClassifierConfFactory
from SecuML.Classification.Configuration.TestConfiguration import TestConfiguration

def aladinMulticlassModelConf():
    classifier_args = {}
    classifier_args['num_folds']            = 4
    classifier_args['sample_weight']        = False
    classifier_args['families_supervision'] = True
    classifier_args['alerts_conf']          = None
    classifier_args['optim_algo']           = 'liblinear'
    test_conf = TestConfiguration()
    test_conf.setUnlabeled(labels_annotations = 'annotations')
    classifier_args['test_conf'] = test_conf
    multiclass_model_conf = ClassifierConfFactory.getFactory().fromParam('LogisticRegression', classifier_args)
    return multiclass_model_conf

class AladinConfiguration(ActiveLearningConfiguration):

    def __init__(self, auto, budget, num_annotations, binary_model_conf):
        ActiveLearningConfiguration.__init__(self, auto, budget)
        self.labeling_method = 'Aladin'
        self.num_annotations = num_annotations
        self.setModelsConf(binary_model_conf)

    def setModelsConf(self, binary_model_conf):
        conf = {}
        conf['binary'] = binary_model_conf
        conf['multiclass'] = aladinMulticlassModelConf()
        ActiveLearningConfiguration.setModelsConf(self, conf)

    def getStrategy(self, iteration):
        return Aladin(iteration)

    def generateSuffix(self):
        suffix  = ''
        suffix += '__' + str(self.num_annotations)
        return suffix

    @staticmethod
    def fromJson(obj, experiment):
        binary_model_conf = ClassifierConfFactory.getFactory().fromJson(
                obj['models_conf']['binary'],
                experiment)
        conf = AladinConfiguration(obj['auto'], obj['budget'],
                                   obj['num_annotations'], binary_model_conf)
        return conf

    def toJson(self):
        conf = ActiveLearningConfiguration.toJson(self)
        conf['__type__']        = 'AladinConfiguration'
        conf['num_annotations'] = self.num_annotations
        return conf

    @staticmethod
    def generateParser(parser):
        al_group = ActiveLearningConfiguration.generateParser(parser)
        al_group.add_argument('--num-annotations',
                type = int,
                default = 100,
                help = 'Number of annotations asked from the user at each iteration.')

    @staticmethod
    def generateParamsFromArgs(args):
        params = ActiveLearningConfiguration.generateParamsFromArgs(args)
        params['num_annotations'] = args.num_annotations
        return params

ActiveLearningConfFactory.getFactory().registerClass('AladinConfiguration', AladinConfiguration)
