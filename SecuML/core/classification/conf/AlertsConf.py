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

from SecuML.core.clustering.conf import ClusteringConfFactory
from SecuML.core.Conf import Conf
from SecuML.core.Conf import exportFieldMethod
from SecuML.core.tools import floats_tools


class AlertsConf(Conf):

    def __init__(self, num_max_alerts, detection_threshold, clustering_conf,
                 logger):
        Conf.__init__(self, logger)
        self.num_max_alerts = num_max_alerts
        self.detection_threshold = detection_threshold
        self.clustering_conf = clustering_conf

    def get_exp_name(self):
        name = '__numMaxAlerts_%d' % self.num_max_alerts
        name += '__detectionThreshold_%s' % \
                floats_tools.toPercentage(self.detection_threshold)
        name += '__%s' % self.clustering_conf.get_exp_name()
        return name

    @staticmethod
    def from_json(obj, logger):
        factory = ClusteringConfFactory.getFactory()
        clustering_conf = factory.from_json(obj['clustering_conf'], logger)
        return AlertsConf(obj['num_max_alerts'], obj['detection_threshold'],
                          clustering_conf, logger)

    def fieldsToExport(self):
        return [('num_max_alerts', exportFieldMethod.primitive),
                ('detection_threshold', exportFieldMethod.primitive),
                ('clustering_conf', exportFieldMethod.obj)]

    @staticmethod
    def generateParser(parser):
        alerts_group = parser.add_argument_group('Alerts parameters')
        alerts_group.add_argument('--detection-threshold',
            type=float,
            default=0.8,
            help='An alert is triggered if the predicted probability of '
                 'maliciousness is above this threshold. '
                 'Default: 0.8.')
        alerts_group.add_argument('--top-n-alerts',
                 default=100,
                 type=int,
                 help='Number of most confident alerts displayed.')
        alerts_group.add_argument('--clustering-algo',
                 default='Kmeans',
                 choices=['Kmeans', 'GaussianMixture'],
                 help='Clustering algorithm to analyze the alerts. '
                      'Default: Kmeans.')
        alerts_group.add_argument('--num-clusters',
                 type=int,
                 default=4,
                 help='Number of clusters built from the alerts. '
                      'Default: 4.')

    @staticmethod
    def fromArgs(args, logger):
        factory = ClusteringConfFactory.getFactory()
        clustering_conf = factory.fromArgs(args.clustering_algo, args, logger)
        return AlertsConf(args.top_n_alerts, args.detection_threshold,
                          clustering_conf, logger)
