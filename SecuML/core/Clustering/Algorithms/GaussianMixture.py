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

import numpy as np
import sklearn.mixture

from SecuML.core.Clustering.ClusteringAlgorithm import ClusteringAlgorithm


class GaussianMixture(ClusteringAlgorithm):

    def __init__(self, instances, conf):
        ClusteringAlgorithm.__init__(self, instances, conf)
        self.algo = sklearn.mixture.GaussianMixture(
            n_components=self.num_clusters,
            covariance_type='diag',
            init_params='kmeans')

    def getDistortion(self):
        return 0

    def getCentroids(self):
        clustering = self.pipeline.named_steps['clustering']
        return clustering.means_

    def getAssignedClusters(self):
        return self.pipeline.predict(self.instances.features.getValues())

    def getPredictedProba(self):
        all_probas = self.pipeline.predict_proba(
            self.instances.features.getValues())
        predicted_proba = np.amax(all_probas, axis=1)
        return predicted_proba

    def getAllProba(self):
        all_probas = self.pipeline.predict_proba(
            self.instances.features.getValues())
        return all_probas
