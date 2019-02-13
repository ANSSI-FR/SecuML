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

from secuml.core.clustering.algos.gaussian_mixture import GaussianMixture
from . import ClusteringConf


class GaussianMixtureConf(ClusteringConf):

    def __init__(self, logger, num_clusters, projection_conf=None):
        ClusteringConf.__init__(self, logger, num_clusters,
                                projection_conf=projection_conf)
        self.algo = GaussianMixture
        self.covariance_type = 'diag'
        self.init_params = 'kmeans'
        self.max_iter = 2

    @staticmethod
    def from_args(args, proj_conf, logger):
        return GaussianMixtureConf(logger, args.num_clusters, proj_conf)

    @staticmethod
    def from_json(obj, proj_conf, logger):
        return GaussianMixtureConf(logger, obj['num_clusters'], proj_conf)
