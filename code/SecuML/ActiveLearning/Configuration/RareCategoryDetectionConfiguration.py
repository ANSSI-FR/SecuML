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
from SecuML.ActiveLearning.QueryStrategies.RareCategoryDetection import RareCategoryDetection

class RareCategoryDetectionConfiguration(ActiveLearningConfiguration):

    def __init__(self, rare_category_detection_conf):
        self.labeling_method = 'RareCategoryDetection'
        self.rare_category_detection_conf = rare_category_detection_conf

    def getStrategy(self, iteration):
        return RareCategoryDetection(iteration)

    def setFixedNumberAnnotations(self, num_malicious, num_benign, cluster_weights):
        self.rare_category_detection_conf.setFixedNumberAnnotations(num_malicious, num_benign, cluster_weights)

    def setNumberAnnotations(self, r):
        self.rare_category_detection_conf.setNumberAnnotations(r)

    def generateSuffix(self):
        suffix = ''
        suffix += self.rare_category_detection_conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj):
        rare_category_detection_conf = InteractiveClusteringConfiguration.fromJson(
                obj['rare_category_detection_conf'])
        conf = RareCategoryDetectionConfiguration(rare_category_detection_conf)
        return conf

    def toJson(self):
        conf = {}
        conf['__type__']                     = 'RareCategoryDetectionConfiguration'
        conf['rare_category_detection_conf'] = self.rare_category_detection_conf.toJson()
        return conf

ActiveLearningConfFactory.getFactory().registerClass('RareCategoryDetectionConfiguration',
        RareCategoryDetectionConfiguration)
