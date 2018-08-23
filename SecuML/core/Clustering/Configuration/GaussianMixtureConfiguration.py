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

from SecuML.core.Clustering.Algorithms.GaussianMixture import GaussianMixture
from SecuML.core.DimensionReduction.Configuration \
        import DimensionReductionConfFactory

from . import ClusteringConfFactory
from .ClusteringConfiguration import ClusteringConfiguration


class GaussianMixtureConfiguration(ClusteringConfiguration):

    def __init__(self, num_clusters, num_results=None, projection_conf=None,
                 label='all', logger=None):
        ClusteringConfiguration.__init__(self,
                                         num_clusters,
                                         num_results=num_results,
                                         projection_conf=projection_conf,
                                         label=label,
                                         logger=logger)
        self.algo = GaussianMixture
        self.covariance_type = 'diag'
        self.init_params = 'kmeans'
        self.max_iter = 2

    @staticmethod
    def fromJson(obj, logger=None):
        conf = GaussianMixtureConfiguration(obj['num_clusters'], logger=logger)
        conf.covariance_type = obj['covariance_type']
        conf.init_params = obj['init_params']
        conf.max_iter = obj['max_iter']
        if obj['projection_conf'] is not None:
            proj_factory = DimensionReductionConfFactory.getFactory()
            projection_conf = proj_factory.fromJson(obj['projection_conf'],
                                                    logger=logger)
            conf.setDimensionReductionConf(projection_conf)
        return conf

    def toJson(self):
        conf = ClusteringConfiguration.toJson(self)
        conf['__type__'] = 'GaussianMixtureConfiguration'
        conf['covariance_type'] = self.covariance_type
        conf['init_params'] = self.init_params
        conf['max_iter'] = self.max_iter
        return conf


ClusteringConfFactory.getFactory().registerClass('GaussianMixtureConfiguration',
                                                 GaussianMixtureConfiguration)
