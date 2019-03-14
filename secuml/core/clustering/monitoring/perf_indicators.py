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

from sklearn import metrics

# The performance indicators are computed only if the ground-truth is
# available.


class PerformanceIndicators(object):

    def gen_eval(self, labels_families, predicted_clusters):
        self.compute_homogeneity_completeness(
            labels_families, predicted_clusters)
        self.compute_adjusted_evaluations(labels_families, predicted_clusters)

    def compute_homogeneity_completeness(self, labels_families,
                                         predicted_clusters):
        if labels_families is None:
            self.homogeneity, self.completeness, self.v_measure = 0, 0, 0
            return
        self.homogeneity, self.completeness, self.v_measure = \
            metrics.homogeneity_completeness_v_measure(labels_families,
                                                       predicted_clusters)

    def compute_adjusted_evaluations(self, labels_families,
                                     predicted_clusters):
        if labels_families is None:
            self.adjusted_rand_score = 0
            self.adjusted_mutual_info_score = 0
            return
        self.adjusted_rand_score = metrics.adjusted_rand_score(
            labels_families, predicted_clusters)
        self.adjusted_mutual_info_score = metrics.adjusted_mutual_info_score(
            labels_families, predicted_clusters, average_method='arithmetic')

    def to_json(self):
        return {'homogeneity': self.homogeneity,
                'completeness': self.completeness,
                'v_measure': self.v_measure,
                'adjusted_rand_score': self.adjusted_rand_score,
                'adjusted_mutual_info_score': self.adjusted_mutual_info_score}
