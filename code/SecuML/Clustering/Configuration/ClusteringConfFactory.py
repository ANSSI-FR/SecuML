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

clustering_conf_factory = None

def getFactory():
    global clustering_conf_factory
    if clustering_conf_factory is None:
        clustering_conf_factory = ClusteringConfFactory()
    return clustering_conf_factory

class ClusteringConfFactory():

    def __init__(self):
        self.register = {}

    def registerClass(self, class_name, class_obj):
        self.register[class_name] = class_obj

    def fromJson(self, obj):
        class_name = obj['__type__']
        obj = self.register[class_name].fromJson(obj)
        return obj

    def fromParam(self, class_name, num_clusters, num_results = None, projection_conf = None, label = 'all'):
        obj = self.register[class_name + 'Configuration'](num_clusters, num_results = num_results,
                projection_conf = projection_conf, label = label)
        return obj
