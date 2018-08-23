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

from SecuML.core.Clustering.Configuration import ClusteringConfFactory
from SecuML.core.Configuration import Configuration


class AlertsConfiguration(Configuration):

    def __init__(self, num_max_alerts, detection_threshold, clustering_conf,
                 logger=None):
        Configuration.__init__(self, logger=logger)
        self.num_max_alerts = num_max_alerts
        self.detection_threshold = detection_threshold
        self.clustering_conf = clustering_conf

    def generateSuffix(self):
        suffix = '__numMaxAlerts_%d__detectionThreshold_%.0f%%' % \
                    (self.num_max_alerts, self.detection_threshold*100)
        suffix += self.clustering_conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj, logger=None):
        clustering_conf = ClusteringConfFactory.getFactory().fromJson(
            obj['clustering_conf'],
            logger=logger)
        conf = AlertsConfiguration(obj['num_max_alerts'],
                                   obj['detection_threshold'],
                                   clustering_conf,
                                   logger=logger)
        return conf

    def toJson(self):
        conf = {}
        conf['__type__'] = 'AlertsConfiguration'
        conf['num_max_alerts'] = self.num_max_alerts
        conf['detection_threshold'] = self.detection_threshold
        conf['clustering_conf'] = self.clustering_conf.toJson()
        return conf
