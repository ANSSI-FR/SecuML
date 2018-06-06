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


class Distortion(object):

    def __init__(self, clustering_algo):
        self.clustering_algo = clustering_algo

    def generateEvaluation(self):
        if self.clustering_algo is None:
            self.global_distortion = None
            self.distortions = None
            return
        # Global distortion
        self.global_distortion = self.clustering_algo.getDistortion()
        # Per cluster distortion
        self.distortions = []
        for c, cluster in enumerate(self.clustering_algo.clustering.clusters):
            distortion = {}
            if cluster.numInstances() > 0:
                distortion['distortion'] = sum(cluster.distances)
                distortion['per_instance_distortion'] = distortion['distortion'] / \
                    cluster.numInstances()
            else:
                distortion['distortion'] = 0
                distortion['per_instance_distortion'] = 0
            self.distortions.append(distortion)

    def toJson(self):
        obj = {}
        obj['global_distortion'] = self.global_distortion
        obj['distortions'] = self.distortions
        return obj
