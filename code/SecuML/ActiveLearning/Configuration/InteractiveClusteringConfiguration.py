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

from SecuML.Classification.Configuration import ClassifierConfFactory
from SecuML.Clustering.Configuration import ClusteringConfFactory

class InteractiveClusteringConfiguration(object):

    def __init__(self, clustering_conf, stop_heterogeneous, semiauto, cluster_strategy):
        self.clustering_conf    = clustering_conf
        self.stop_heterogeneous = stop_heterogeneous
        self.semiauto           = semiauto
        self.cluster_strategy   = cluster_strategy

    def setFixedNumberAnnotations(self, num_annotations, cluster_weights):
        self.num_annotations = num_annotations
        self.cluster_weights = cluster_weights
        self.r               = None

    def setNumberAnnotations(self, r):
        self.r               = r
        self.num_annotations = None
        self.cluster_weights = None

    def generateSuffix(self):
        suffix = ''
        suffix += self.clustering_conf.generateSuffix()
        if self.r is not None:
            suffix += '__r' + str(self.r)
        else:
            suffix += '__numAnnotations' + str(self.num_annotations)
        suffix += '__clusterStrategy_' + self.cluster_strategy
        if self.cluster_weights is not None:
            suffix += '__clusterWeights' + self.cluster_weights
        if self.stop_heterogeneous:
            suffix += '__stopHeterogeneous'
        if self.semiauto:
            suffix += '__semiAutoLabels'
        return suffix

    @staticmethod
    def fromJson(obj):
        try:
            clustering_conf = ClusteringConfFactory.getFactory().fromJson(obj['clustering_conf'])
        except:
            clustering_conf = ClassifierConfFactory.getFactory().fromJson(obj['clustering_conf'], None)
        conf = InteractiveClusteringConfiguration(clustering_conf, obj['stop_heterogeneous'], obj['semiauto'],
                obj['cluster_strategy'])
        if obj['r'] is not None:
            conf.setNumberAnnotations(obj['r'])
        else:
            conf.setFixedNumberAnnotations(obj['num_annotations'], obj['cluster_weights'])
        return conf

    def toJson(self):
        conf = {}
        conf['__type__'] = 'InteractiveClusteringConfiguration'
        conf['stop_heterogeneous'] = self.stop_heterogeneous
        conf['semiauto']           = self.semiauto
        conf['cluster_strategy']   = self.cluster_strategy
        conf['clustering_conf']    = self.clustering_conf.toJson()
        conf['num_annotations']    = self.num_annotations
        conf['cluster_weights']    = self.cluster_weights
        conf['r']                  = self.r
        return conf
