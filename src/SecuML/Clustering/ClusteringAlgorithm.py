## SecuML
## Copyright (C) 2016-2017  ANSSI
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

import abc
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from Clustering import Clustering

class ClusteringAlgorithm(object):

    def __init__(self, instances, conf):
        self.instances    = instances
        self.conf         = conf
        self.num_clusters = self.conf.num_clusters
        self.clustering   = None

    @abc.abstractmethod
    def getDistortion(self):
        return

    @abc.abstractmethod
    def getCentroids(self):
        return

    @abc.abstractmethod
    def getAssignedClusters(self):
        return

    def getPredictedProba(self):
        return None

    def getAllProba(self):
        return None

    def fit(self):
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('clustering', self.algo)])
        self.pipeline.fit(self.instances.getFeatures())

    def export(self, output_directory, quick = False, drop_annotated_instances = False):
        self.clustering = Clustering(self.instances, self.getAssignedClusters(),
                                     clustering_algo = self)
        self.clustering.generateClustering(self.getAllProba(),
                                           self.getCentroids(),
                                           drop_annotated_instances = drop_annotated_instances)
        self.clustering.export(output_directory)
        self.clustering.generateEvaluation(output_directory, quick = quick)
