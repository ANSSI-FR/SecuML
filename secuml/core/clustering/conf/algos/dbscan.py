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

from secuml.core.clustering.algos.dbscan import Dbscan
from secuml.core.conf import exportFieldMethod
from . import ClusteringConf


class DbscanConf(ClusteringConf):

    def __init__(self, logger, metric, projection_conf=None):
        ClusteringConf.__init__(self, logger, None,
                                projection_conf=projection_conf)
        self.algo = Dbscan
        self.metric = metric

    def fields_to_export(self):
        fields = ClusteringConf.fields_to_export(self)
        fields.append(('metric', exportFieldMethod.primitive))
        return fields

    @staticmethod
    def gen_parser(parser):
        ClusteringConf.gen_parser(parser)
        parser.add_argument('--metric',
                            choices=['euclidean', 'cosine'],
                            default='euclidean')

    @staticmethod
    def from_args(args, proj_conf, logger):
        return DbscanConf(logger, args.metric, projection_conf=proj_conf)

    @staticmethod
    def from_json(obj, proj_conf, logger):
        return DbscanConf(logger, obj['metric'], projection_conf=proj_conf)
