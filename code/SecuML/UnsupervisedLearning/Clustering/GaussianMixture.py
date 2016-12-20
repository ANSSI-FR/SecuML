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

import sklearn.mixture

from ClusteringAlgorithm import ClusteringAlgorithm

class GaussianMixture(ClusteringAlgorithm):

    def __init__(self, instances, experiment):
        ClusteringAlgorithm.__init__(self, instances, experiment)
        self.algo = sklearn.mixture.GaussianMixture(
                n_components = self.num_clusters, 
                covariance_type = 'diag',
                init_params = 'kmeans')
    
    def getDistortion(self):
        return 0
            
    def getCentroid(self, cluster):
        clustering = self.pipeline.named_steps['clustering']
        return clustering.means_[cluster, ] 
    
    def getLabels(self):
        return self.pipeline.predict(self.instances.getFeatures())
