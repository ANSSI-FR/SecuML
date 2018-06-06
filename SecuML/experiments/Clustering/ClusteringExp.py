# SecuML
# Copyright (C) 2018  ANSSI
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

import json

from SecuML.core.Clustering.Clustering import Clustering

from .ClusterExp import ClusterExp


class ClusteringExp(Clustering):

    def initClustersList(self, num_clusters):
        self.clusters = [ClusterExp() for x in range(num_clusters)]

    @staticmethod
    def fromJson(directory):
        clustering = ClusteringExp(None, [])
        with open(directory + 'clusters.json', 'r') as f:
            obj = json.load(f)
            clustering.assigned_clusters = obj['assigned_clusters']
            clustering.num_clusters = len(obj) - 1
            clustering.clusters = [
                None for x in range(clustering.num_clusters)]
            for c in range(clustering.num_clusters):
                clustering.clusters[c] = ClusterExp.fromJson(obj[str(c)])
        return clustering

    def getClusterLabelsFamilies(self, experiment, selected_cluster):
        cluster = self.clusters[selected_cluster]
        return cluster.getClusterLabelsFamilies(experiment)

    def getClusterLabelFamilyIds(self, experiment, selected_cluster,
                                 label, family):
        return self.clusters[selected_cluster].getClusterLabelFamilyIds(
            experiment,
            label, family)
