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
from RareCategoryDetectionStrategy import RareCategoryDetectionStrategy
from SecuML.ActiveLearning.QueryStrategies.Ilab import Ilab
from SecuML.Classification.Configuration import ClassifierConfFactory
from SecuML.Classification.Configuration.TestConfiguration import TestConfiguration

class IlabConfiguration(ActiveLearningConfiguration):

    def __init__(self, auto, budget, rare_category_detection_conf, num_uncertain, eps, binary_model_conf):
        ActiveLearningConfiguration.__init__(self, auto, budget)
        self.labeling_method              = 'Ilab'
        self.eps                          = eps
        self.num_uncertain                = num_uncertain
        self.rare_category_detection_conf = rare_category_detection_conf
        self.setBinaryModelConf(binary_model_conf)

    def setBinaryModelConf(self, binary_model_conf):
        conf = {}
        conf['binary'] = binary_model_conf
        ActiveLearningConfiguration.setModelsConf(self, conf)

    def getStrategy(self, iteration):
        return Ilab(iteration)

    def generateSuffix(self):
        suffix = ''
        suffix += self.rare_category_detection_conf.generateSuffix()
        suffix += '__numUnsure' + str(self.num_uncertain)
        return suffix

    @staticmethod
    def fromJson(obj, experiment):
        rare_category_detection_conf = RareCategoryDetectionStrategy.fromJson(obj['rare_category_detection_conf'])
        binary_model_conf = ClassifierConfFactory.getFactory().fromJson(obj['models_conf']['binary'], experiment)
        conf = IlabConfiguration(obj['auto'], obj['budget'],
                                 rare_category_detection_conf,
                                 obj['num_uncertain'], obj['eps'],
                                 binary_model_conf)
        return conf

    def toJson(self):
        conf = ActiveLearningConfiguration.toJson(self)
        conf['__type__']                     = 'IlabConfiguration'
        conf['eps']                          = self.eps
        conf['num_uncertain']                = self.num_uncertain
        conf['rare_category_detection_conf'] = self.rare_category_detection_conf.toJson()
        return conf

    @staticmethod
    def generateParser(parser):
        al_group = ActiveLearningConfiguration.generateParser(parser)
        al_group.add_argument('--num-uncertain',
                type = int,
                default = 10,
                help = 'Number of instances queried close to the decision boundary.')
        al_group.add_argument('--num-annotations',
                type = int,
                default = 45,
                help = 'Number of instances queried for each family.')
        al_group.add_argument('--cluster-strategy',
                default = 'center_anomalous')

    @staticmethod
    def generateParamsFromArgs(args):
        params = ActiveLearningConfiguration.generateParamsFromArgs(args)
        multiclass_classifier_args = {}
        multiclass_classifier_args['num_folds']            = args.num_folds
        multiclass_classifier_args['sample_weight']        = False
        multiclass_classifier_args['families_supervision'] = True
        test_conf = TestConfiguration()
        test_conf.setUnlabeled(labels_annotations = 'annotations')
        multiclass_classifier_args['test_conf'] = test_conf
        multiclass_conf = ClassifierConfFactory.getFactory().fromParam(
                'LogisticRegression', multiclass_classifier_args)
        rare_category_detection_conf = RareCategoryDetectionStrategy(multiclass_conf,
                args.cluster_strategy, args.num_annotations, 'uniform')
        params['rare_category_detection_conf'] = rare_category_detection_conf
        params['num_uncertain'] = args.num_uncertain
        params['eps'] = 0.49
        return params


ActiveLearningConfFactory.getFactory().registerClass('IlabConfiguration', IlabConfiguration)
