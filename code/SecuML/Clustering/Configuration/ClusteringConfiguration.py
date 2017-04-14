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

from SecuML.Projection.Configuration import ProjectionConfFactory

import ClusteringConfFactory

class ClusteringConfiguration(object):

    def __init__(self, num_clusters, num_results = None, projection_conf = None, label = 'all'):
        self.num_clusters = num_clusters
        if num_results is not None:
            self.num_results = num_results
        else:
            self.num_results = 10
        self.projection_conf = projection_conf
        self.label = label

    def setProjectionConf(self, projection_conf):
        self.projection_conf = projection_conf

    def setNumClusters(self, num_clusters):
        self.num_clusters = num_clusters

    def generateSuffix(self):
        suffix  = '__' + str(self.num_clusters)
        suffix += '_' + self.algo.__name__
        if self.projection_conf is not None:
            suffix += self.projection_conf.generateSuffix()
        if self.label != 'all':
            suffix += '__' + self.label
        return suffix

    @staticmethod
    def fromJson(obj, exp):
        conf = ClusteringConfiguration(obj['num_clusters'], num_results = obj['num_results'], label = obj['label'])
        if obj['projection_conf'] is not None:
            projection_conf = ProjectionConfFactory.getFactory().fromJson(obj['projection_conf'])
            conf.setProjectionConf(projection_conf)
        return conf

    def toJson(self):
        conf = {}
        conf['__type__'] = 'ClusteringConfiguration'
        conf['num_clusters'] = self.num_clusters
        conf['num_results'] = self.num_results
        conf['projection_conf'] = None
        if self.projection_conf is not None:
            conf['projection_conf'] = self.projection_conf.toJson()
        conf['label'] = self.label
        return conf

ClusteringConfFactory.getFactory().registerClass('ClusteringConfiguration',
        ClusteringConfiguration)
