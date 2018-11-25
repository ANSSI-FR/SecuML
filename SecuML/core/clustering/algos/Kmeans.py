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

import sklearn.cluster

from SecuML.core.clustering.ClusteringAlgorithm import ClusteringAlgorithm


class Kmeans(ClusteringAlgorithm):

    def __init__(self, instances, conf, algo='auto'):
        n_jobs = -1
        ClusteringAlgorithm.__init__(self, instances, conf)
        self.algo = sklearn.cluster.KMeans(
            n_clusters=self.num_clusters,
            n_jobs=n_jobs, verbose=0,
            algorithm=algo)

    def getDistortion(self):
        return self.algo.inertia_

    def getCentroids(self):
        clustering = self.pipeline.named_steps['clustering']
        return clustering.cluster_centers_

    def getAssignedClusters(self):
        return self.pipeline.predict(self.instances.features.getValues())
