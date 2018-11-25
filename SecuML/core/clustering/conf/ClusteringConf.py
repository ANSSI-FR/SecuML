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

from SecuML.core.Conf import Conf
from SecuML.core.Conf import exportFieldMethod
from SecuML.core.projection.conf import ProjectionConfFactory

from . import ClusteringConfFactory


class ClusteringConf(Conf):

    def __init__(self, logger, num_clusters, projection_conf=None):
        Conf.__init__(self, logger)
        self.num_clusters = num_clusters
        self.projection_conf = projection_conf
        self.algo = None

    def setNumClusters(self, num_clusters):
        self.num_clusters = num_clusters

    def get_exp_name(self):
        name = self.algo.__name__
        name += '__numClusters_%d' % self.num_clusters
        if self.projection_conf is not None:
            name += '__%s' % self.projection_conf.get_exp_name()
        return name

    def fieldsToExport(self):
        return [('num_clusters', exportFieldMethod.primitive),
                ('projection_conf', exportFieldMethod.obj),
                ('algo', exportFieldMethod.obj_class)]

    @staticmethod
    def generateParser(parser):
        # Clustering arguments
        parser.add_argument('--num-clusters',
                            type=int,
                            default=4)
        # Projection parameters
        projection_group = parser.add_argument_group('Projection parameters')
        projection_group.add_argument('--projection-algo',
                 choices=['Pca', 'Rca', 'Lda',
                          'Lmnn', 'Nca', 'Itml', None],
                 default=None,
                 help='Projection performed before building the clustering. '
                      'By default the instances are not projected.')
        projection_group.add_argument('--families-supervision',
                 action='store_true',
                 default=False,
                 help='When set to True, the semi-supervision is based on the '
                 'families instead of the binary labels. '
                 'Useless if an unsupervised projection method is used.')
        projection_group.add_argument('--num-components',
                                      type=int,
                                      default=None)

    @staticmethod
    def proj_conf_from_args(args, logger):
        if not hasattr(args, 'projection_algo') or args.projection_algo is None:
            return None
        proj_factory = ProjectionConfFactory.getFactory()
        proj_conf = proj_factory.fromArgs(args.projection_algo, args, logger)
        return proj_conf

    @staticmethod
    def from_json(obj, logger):
        projection_conf = None
        if obj['projection_conf'] is not None:
            proj_factory = ProjectionConfFactory.getFactory()
            projection_conf = proj_factory.from_json(obj['projection_conf'],
                                                    logger)
        return ClusteringConf(logger, obj['num_clusters'],
                              projection_conf=projection_conf)


ClusteringConfFactory.getFactory().registerClass('ClusteringConf',
                                                 ClusteringConf)
