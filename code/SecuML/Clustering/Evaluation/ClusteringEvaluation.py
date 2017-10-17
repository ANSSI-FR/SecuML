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

from Distortion import Distortion
from Silhouette import Silhouette
from PerformanceIndicators import PerformanceIndicators

class ClusteringEvaluation(object):

    def __init__(self, instances, assigned_clusters, clustering_algo):
        self.instances         = instances
        self.assigned_clusters = assigned_clusters
        self.distortion        = Distortion(clustering_algo)
        self.silhouette        = Silhouette(instances)
        self.performance       = PerformanceIndicators()

    def generateEvaluation(self, output_dir, quick = False):
        self.distortion.generateEvaluation()
        self.silhouette.generateEvaluation(output_dir, self.assigned_clusters, quick = quick)
        if self.instances.true_labels is not None:
            true_labels = self.instances.getLabels(true_labels = True)
            true_families = self.instances.getFamilies(true_labels = True)
            labels_families = [str(x[0]) + '_' + str(x[1]) for x in zip(true_labels, true_families)]
        else:
            labels_families = None
        self.performance.generateEvaluation(labels_families, self.assigned_clusters)

    def toJson(self):
        obj = {}
        obj['distortion']  = self.distortion.toJson()
        obj['silhouette']  = self.silhouette.toJson()
        obj['performance'] = self.performance.toJson()
        return obj
