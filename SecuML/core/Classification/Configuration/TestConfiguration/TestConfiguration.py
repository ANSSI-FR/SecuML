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

from SecuML.core.Configuration import Configuration
from SecuML.core.Clustering.Configuration import ClusteringConfFactory
from SecuML.core.Classification.Configuration.AlertsConfiguration \
        import AlertsConfiguration


class TestConfiguration(Configuration):

    def __init__(self, alerts_conf=None, logger=None):
        Configuration.__init__(self, logger=logger)
        self.method = None
        self.alerts_conf = alerts_conf

    def generateSuffix(self):
        if self.alerts_conf is not None:
            return self.alerts_conf.generateSuffix()
        else:
            return ''

    @staticmethod
    def alertConfFromJson(obj, logger=None):
        if obj['alerts_conf'] is not None:
            alerts_conf = AlertsConfiguration.fromJson(
                        obj['alerts_conf'],
                        logger=logger)
            return alerts_conf
        else:
            return None

    def toJson(self):
        conf = {}
        conf['__type__'] = 'TestConfiguration'
        conf['method'] = self.method
        conf['alerts_conf'] = None
        if self.alerts_conf is not None:
            conf['alerts_conf'] = self.alerts_conf.toJson()
        return conf

    @staticmethod
    def generateParamsFromArgs(args, logger=None):
        params = {}
        params['num_clusters'] = args.num_clusters
        params['num_results'] = None
        params['projection_conf'] = None
        params['label'] = 'all'
        clustering_conf = ClusteringConfFactory.getFactory().fromParam(
                args.clustering_algo,
                params,
                logger=logger)
        alerts_conf = AlertsConfiguration(args.top_n_alerts,
                                          args.detection_threshold,
                                          clustering_conf,
                                          logger=logger)
        params['alerts_conf'] = alerts_conf
        return params
