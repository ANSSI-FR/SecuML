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

import numpy as np
import sklearn.mixture

from . import ClusteringAlgorithm


class GaussianMixture(ClusteringAlgorithm):

    def __init__(self, instances, conf):
        ClusteringAlgorithm.__init__(self, instances, conf)
        self.algo = sklearn.mixture.GaussianMixture(
            n_components=self.num_clusters,
            covariance_type='diag',
            init_params='kmeans')

    def get_distortion(self):
        return 0

    def get_centroids(self):
        return self.pipeline['clustering'].means_

    def get_predicted_proba(self):
        all_probas = self.get_all_proba()
        return np.amax(all_probas, axis=1)

    def get_all_proba(self):
        features = self.instances.features.get_values()
        return self.pipeline.predict_proba(features)
