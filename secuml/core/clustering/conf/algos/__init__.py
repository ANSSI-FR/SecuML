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

from secuml.core.conf import Conf
from secuml.core.conf import ConfFactory
from secuml.core.conf import exportFieldMethod
from secuml.core.projection.conf import algos as projection_conf


class ClusteringConf(Conf):

    def __init__(self, logger, num_clusters, projection_conf=None):
        Conf.__init__(self, logger)
        self.num_clusters = num_clusters
        self.projection_conf = projection_conf
        self.algo = None

    def set_num_clusters(self, num_clusters):
        self.num_clusters = num_clusters

    def get_exp_name(self):
        name = '%s__num_clusters_%d' % (self.algo.__name__, self.num_clusters)
        if self.projection_conf is not None:
            name += '__%s' % self.projection_conf.get_exp_name()
        return name

    def fields_to_export(self):
        return [('num_clusters', exportFieldMethod.primitive),
                ('projection_conf', exportFieldMethod.obj),
                ('algo', exportFieldMethod.obj_class)]

    @staticmethod
    def gen_parser(parser):
        # Clustering arguments
        parser.add_argument('--num-clusters',
                            type=int,
                            default=4)
        # Projection parameters
        projection_group = parser.add_argument_group('Projection parameters')
        projection_group.add_argument(
                '--projection-algo',
                choices=projection_conf.get_factory().get_methods() + [None],
                default=None,
                help='Projection performed before building the clustering. '
                     'By default the instances are not projected.')
        projection_group.add_argument(
                '--multiclass',
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
        if (not hasattr(args, 'projection_algo')
                or args.projection_algo is None):
            return None
        proj_factory = projection_conf.get_factory()
        proj_conf = proj_factory.from_args(args.projection_algo, args, logger)
        return proj_conf

    @staticmethod
    def from_json(obj, proj_conf, logger):
        return ClusteringConf(logger, obj['num_clusters'],
                              projection_conf=proj_conf)


clustering_conf_factory = None


def get_factory():
    global clustering_conf_factory
    if clustering_conf_factory is None:
        clustering_conf_factory = ClusteringConfFactory()
    return clustering_conf_factory


class ClusteringConfFactory(ConfFactory):

    def from_args(self, method, args, logger):
        if (not hasattr(args, 'projection_algo')
                or args.projection_algo is None):
            proj_conf = None
        else:
            proj_factory = projection_conf.get_factory()
            proj_conf = proj_factory.from_args(args.projection_algo, args,
                                               logger)
        class_ = self.methods[method + 'Conf']
        return class_.from_args(args, proj_conf, logger)

    def from_json(self, obj, logger):
        proj_conf = None
        if obj['projection_conf'] is not None:
            proj_factory = projection_conf.get_factory()
            proj_conf = proj_factory.from_json(obj['projection_conf'], logger)
        class_ = self.methods[obj['__type__']]
        return class_.from_json(obj, proj_conf, logger)

    def get_methods(self):
        algos = ConfFactory.get_methods(self)
        algos.remove('Clustering')
        return algos


get_factory().register('ClusteringConf', ClusteringConf)
