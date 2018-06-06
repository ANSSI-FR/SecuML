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

from SecuML.core.Clustering.Algorithms.Kmeans import Kmeans
from SecuML.core.DimensionReduction.Configuration import DimensionReductionConfFactory

from . import ClusteringConfFactory
from .ClusteringConfiguration import ClusteringConfiguration


class KmeansConfiguration(ClusteringConfiguration):

    def __init__(self, num_clusters, num_results=None, projection_conf=None,
                 label='all', logger=None):
        ClusteringConfiguration.__init__(self, num_clusters,
                                         num_results=num_results,
                                         projection_conf=projection_conf,
                                         label=label,
                                         logger=logger)
        self.algo = Kmeans

    @staticmethod
    def fromJson(obj):
        conf = KmeansConfiguration(obj['num_clusters'])
        if obj['projection_conf'] is not None:
            projection_conf = DimensionReductionConfFactory.getFactory(
            ).fromJson(obj['projection_conf'])
            conf.setDimensionReductionConf(projection_conf)
        return conf

    def toJson(self):
        conf = ClusteringConfiguration.toJson(self)
        conf['__type__'] = 'KmeansConfiguration'
        return conf


ClusteringConfFactory.getFactory().registerClass('KmeansConfiguration',
                                                 KmeansConfiguration)
