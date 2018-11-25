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

from SecuML.core.clustering.algos.GaussianMixture import GaussianMixture
from SecuML.core.projection.conf import ProjectionConfFactory

from . import ClusteringConfFactory
from .ClusteringConf import ClusteringConf


class GaussianMixtureConf(ClusteringConf):

    def __init__(self, logger, num_clusters, projection_conf=None):
        ClusteringConf.__init__(self, logger, num_clusters,
                                projection_conf=projection_conf)
        self.algo = GaussianMixture
        self.covariance_type = 'diag'
        self.init_params = 'kmeans'
        self.max_iter = 2

    @staticmethod
    def fromArgs(args, logger):
        proj_conf = ClusteringConf.proj_conf_from_args(args, logger)
        return GaussianMixtureConf(logger, args.num_clusters, proj_conf)

    @staticmethod
    def from_json(obj, logger):
        projection_conf = None
        if obj['projection_conf'] is not None:
            proj_factory = ProjectionConfFactory.getFactory()
            projection_conf = proj_factory.from_json(obj['projection_conf'],
                                                    logger)
        return GaussianMixtureConf(logger, obj['num_clusters'],
                                   projection_conf=projection_conf)


ClusteringConfFactory.getFactory().registerClass('GaussianMixtureConf',
                                                 GaussianMixtureConf)
