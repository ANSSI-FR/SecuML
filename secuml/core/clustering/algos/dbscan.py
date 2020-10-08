# SecuML
# Copyright (C) 2016-2019  ANSSI
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

from . import ClusteringAlgorithm


class Dbscan(ClusteringAlgorithm):

    def __init__(self, instances, conf):
        n_jobs = -1
        ClusteringAlgorithm.__init__(self, instances, conf)
        self.algo = sklearn.cluster.DBSCAN(n_jobs=n_jobs, metric=conf.metric)

    def get_distortion(self):
        return 0

    def get_centroids(self):
        return None

    def get_assigned_clusters(self):
        return self.pipeline.fit_predict(self.instances.features.get_values())
