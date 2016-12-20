## SecuML
## Copyright (C) 2016  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

from SecuML.UnsupervisedLearning.Configuration import ClusteringConfFactory

class AlertsConfiguration(object):

    def __init__(self, num_max_alerts, detection_threshold, clustering_conf):
        self.num_max_alerts = num_max_alerts
        self.detection_threshold = detection_threshold
        self.clustering_conf = clustering_conf

    def generateSuffix(self):
        suffix  = '__numMaxAlerts_' + str(self.num_max_alerts)
        suffix += '__detectionThreshold_' + str(int(self.detection_threshold * 100))
        suffix += self.clustering_conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj):
        clustering_conf = ClusteringConfFactory.getFactory().fromJson(
                obj['clustering_conf'])
        conf = AlertsConfiguration(obj['num_max_alerts'], obj['detection_threshold'],
                clustering_conf)
        return conf

    def toJson(self):
        conf = {}
        conf['__type__'] = 'AlertsConfiguration'
        conf['num_max_alerts'] = self.num_max_alerts
        conf['detection_threshold'] = self.detection_threshold
        conf['clustering_conf'] = self.clustering_conf.toJson()
        return conf
