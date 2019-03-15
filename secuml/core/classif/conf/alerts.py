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

from secuml.core.clustering.conf import algos as cluster_conf
from secuml.core.conf import Conf
from secuml.core.conf import exportFieldMethod
from secuml.core.tools.float import to_percentage


class AlertsConf(Conf):

    def __init__(self, detection_threshold, clustering_conf, logger):
        Conf.__init__(self, logger)
        self.detection_threshold = detection_threshold
        self.clustering_conf = clustering_conf

    def get_exp_name(self):
        return '__detectionThreshold_%s__%s' % (
                to_percentage(self.detection_threshold),
                self.clustering_conf.get_exp_name())

    @staticmethod
    def from_json(obj, logger):
        factory = cluster_conf.get_factory()
        clustering_conf = factory.from_json(obj['clustering_conf'], logger)
        return AlertsConf(obj['detection_threshold'], clustering_conf, logger)

    def fields_to_export(self):
        return [('detection_threshold', exportFieldMethod.primitive),
                ('clustering_conf', exportFieldMethod.obj)]

    @staticmethod
    def gen_parser(parser):
        alerts_group = parser.add_argument_group('Alerts parameters')
        alerts_group.add_argument(
            '--detection-threshold',
            type=float,
            default=0.8,
            help='An alert is triggered if the predicted probability of '
                 'maliciousness is above this threshold. '
                 'Default: 0.8.')
        alerts_group.add_argument(
                 '--clustering-algo',
                 default='Kmeans',
                 choices=['Kmeans', 'GaussianMixture'],
                 help='Clustering algorithm to analyze the alerts. '
                      'Default: Kmeans.')
        alerts_group.add_argument(
                 '--num-clusters',
                 type=int,
                 default=4,
                 help='Number of clusters built from the alerts. '
                      'Default: 4.')

    @staticmethod
    def from_args(args, logger):
        factory = cluster_conf.get_factory()
        clustering_conf = factory.from_args(args.clustering_algo, args, logger)
        return AlertsConf(args.detection_threshold, clustering_conf, logger)
