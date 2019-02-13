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

from .distortion import Distortion
from .silhouette import Silhouette
from .perf_indicators import PerformanceIndicators


class ClusteringEvaluation(object):

    def __init__(self, instances, assigned_clusters, clustering_algo):
        self.instances = instances
        self.assigned_clusters = assigned_clusters
        self.distortion = Distortion(clustering_algo)
        self.silhouette = Silhouette(instances)
        self.performance = PerformanceIndicators()

    def gen_eval(self, output_dir, quick=False):
        self.distortion.gen_eval()
        self.silhouette.gen_eval(output_dir, self.assigned_clusters,
                                 quick=quick)
        if self.instances.has_ground_truth():
            gt_labels = self.instances.ground_truth.get_labels()
            gt_families = self.instances.ground_truth.get_families()
            labels_families = [str(x[0]) + '_' + str(x[1])
                               for x in zip(gt_labels, gt_families)]
        else:
            labels_families = None
        self.performance.gen_eval(labels_families, self.assigned_clusters)

    def to_json(self):
        return {'distortion': self.distortion.to_json(),
                'silhouette': self.silhouette.to_json(),
                'performance': self.performance.to_json()}
