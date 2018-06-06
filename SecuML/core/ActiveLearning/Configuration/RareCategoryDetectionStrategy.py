# SecuML
# Copyright (C) 2016  ANSSI
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

from SecuML.core.Classification.Configuration import ClassifierConfFactory


class RareCategoryDetectionStrategy(object):

    def __init__(self, classification_conf, cluster_strategy, num_annotations, cluster_weights):
        self.classification_conf = classification_conf
        self.cluster_strategy = cluster_strategy
        self.num_annotations = num_annotations
        self.cluster_weights = cluster_weights

    def generateSuffix(self):
        suffix = ''
        suffix += self.classification_conf.generateSuffix()
        suffix += '__numAnnotations' + str(self.num_annotations)
        suffix += '__clusterStrategy_' + self.cluster_strategy
        suffix += '__clusterWeights' + self.cluster_weights
        return suffix

    @staticmethod
    def fromJson(obj):
        classification_conf = ClassifierConfFactory.getFactory(
        ).fromJson(obj['classification_conf'])
        conf = RareCategoryDetectionStrategy(classification_conf, obj['cluster_strategy'],
                                             obj['num_annotations'], obj['cluster_weights'])
        return conf

    def toJson(self):
        conf = {}
        conf['__type__'] = 'RareCategoryDetectionStrategy'
        conf['classification_conf'] = self.classification_conf.toJson()
        conf['cluster_strategy'] = self.cluster_strategy
        conf['num_annotations'] = self.num_annotations
        conf['cluster_weights'] = self.cluster_weights
        return conf
