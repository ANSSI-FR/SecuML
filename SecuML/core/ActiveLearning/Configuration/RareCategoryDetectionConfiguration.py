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
from .RareCategoryDetectionStrategy import RareCategoryDetectionStrategy

from SecuML.core.ActiveLearning.QueryStrategies.RareCategoryDetection import RareCategoryDetection
from SecuML.core.Classification.Configuration import ClassifierConfFactory
from SecuML.core.Classification.Configuration.TestConfiguration.UnlabeledLabeledConf import UnlabeledLabeledConf
from SecuML.core.Classification.Configuration.TestConfiguration.ValidationDatasetConf import ValidationDatasetConf


class RareCategoryDetectionConfiguration(ActiveLearningConfiguration):

    def __init__(self, auto, budget, rare_category_detection_conf, multiclass_model_conf, validation_conf, logger=None):
        ActiveLearningConfiguration.__init__(
            self, auto, budget, validation_conf, logger=logger)
        self.query_strategy = 'RareCategoryDetection'
        self.rare_category_detection_conf = rare_category_detection_conf
        self.setMulticlassModelConf(multiclass_model_conf)

    def setMulticlassModelConf(self, multiclass_model_conf):
        conf = {}
        conf['multiclass'] = multiclass_model_conf
        ActiveLearningConfiguration.setModelsConf(self, conf)

    def getStrategy(self, iteration):
        return RareCategoryDetection(iteration)

    def generateSuffix(self):
        suffix = ''
        suffix += self.rare_category_detection_conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj):
        validation_conf = None
        if obj['validation_conf'] is not None:
            validation_conf = ValidationDatasetConf.fromJson(
                obj['validation_conf'])
        multiclass_model_conf = ClassifierConfFactory.getFactory(
        ).fromJson(obj['models_conf']['multiclass'])
        rare_category_detection_conf = RareCategoryDetectionStrategy.fromJson(
            obj['rare_category_detection_conf'])
        conf = RareCategoryDetectionConfiguration(obj['auto'], obj['budget'],
                                                  rare_category_detection_conf,
                                                  multiclass_model_conf,
                                                  validation_conf)
        return conf

    def toJson(self):
        conf = ActiveLearningConfiguration.toJson(self)
        conf['__type__'] = 'RareCategoryDetectionConfiguration'
        conf['rare_category_detection_conf'] = self.rare_category_detection_conf.toJson()
        return conf

    @staticmethod
    def generateParser(parser):
        al_group = ActiveLearningConfiguration.generateParser(
            parser, binary=False)
        al_group.add_argument('--num-annotations',
                              type=int,
                              default=100,
                              help='Number of instances queried for each family.')
        al_group.add_argument('--cluster-strategy',
                              default='center_anomalous')

    @staticmethod
    def generateParamsFromArgs(args):
        params = ActiveLearningConfiguration.generateParamsFromArgs(args)
        multiclass_classifier_args = {}
        multiclass_classifier_args['num_folds'] = args.num_folds
        multiclass_classifier_args['sample_weight'] = False
        multiclass_classifier_args['families_supervision'] = True
        multiclass_classifier_args['alerts_conf'] = None
        test_conf = UnlabeledLabeledConf()
        multiclass_classifier_args['test_conf'] = test_conf
        multiclass_conf = ClassifierConfFactory.getFactory().fromParam(
            args.model_class, multiclass_classifier_args)
        rare_category_detection_conf = RareCategoryDetectionStrategy(multiclass_conf,
                                                                     args.cluster_strategy, args.num_annotations, 'uniform')
        params['rare_category_detection_conf'] = rare_category_detection_conf
        params['num_annotations'] = args.num_annotations
        params['multiclass_model_conf'] = multiclass_conf
        return params


ActiveLearningConfFactory.getFactory().registerClass('RareCategoryDetectionConfiguration',
                                                     RareCategoryDetectionConfiguration)
