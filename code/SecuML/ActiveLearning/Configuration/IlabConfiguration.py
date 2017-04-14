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
from InteractiveClusteringConfiguration import InteractiveClusteringConfiguration
from SecuML.ActiveLearning.QueryStrategies.Ilab import Ilab

class IlabConfiguration(ActiveLearningConfiguration):

    def __init__(self, rare_category_detection_conf, num_annotations, num_uncertain, eps, train_semiauto):
        self.labeling_method              = 'Ilab'
        self.eps                          = eps
        self.train_semiauto               = train_semiauto
        self.num_uncertain                = num_uncertain
        self.rare_category_detection_conf = rare_category_detection_conf

    def getStrategy(self, iteration):
        return Ilab(iteration)

    def setFixedNumberAnnotations(self, num_malicious, num_benign, cluster_weights):
        self.rare_category_detection_conf.setFixedNumberAnnotations(num_malicious, num_benign, cluster_weights)

    def setNumberAnnotations(self, r):
        self.rare_category_detection_conf.setNumberAnnotations(r)

    def generateSuffix(self):
        suffix = ''
        suffix += self.rare_category_detection_conf.generateSuffix()
        suffix += '__numUnsure' + str(self.num_uncertain)
        if self.train_semiauto:
            suffix += '__trainSemiAuto'
        return suffix

    @staticmethod
    def fromJson(obj):
        rare_category_detection_conf = InteractiveClusteringConfiguration.fromJson(
                obj['rare_category_detection_conf'])
        conf = IlabConfiguration(rare_category_detection_conf, None, obj['num_uncertain'], obj['eps'],
                obj['train_semiauto'])
        return conf

    def toJson(self):
        conf = {}
        conf['__type__']                     = 'IlabConfiguration'
        conf['eps']                          = self.eps
        conf['train_semiauto']               = self.train_semiauto
        conf['num_uncertain']                = self.num_uncertain
        conf['rare_category_detection_conf'] = self.rare_category_detection_conf.toJson()
        return conf

ActiveLearningConfFactory.getFactory().registerClass('IlabConfiguration', IlabConfiguration)
