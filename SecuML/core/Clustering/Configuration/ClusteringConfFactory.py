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

import inspect

clustering_conf_factory = None


def getFactory():
    global clustering_conf_factory
    if clustering_conf_factory is None:
        clustering_conf_factory = ClusteringConfFactory()
    return clustering_conf_factory


class ClusteringConfFactory(object):

    def __init__(self):
        self.register = {}

    def registerClass(self, class_name, class_obj):
        self.register[class_name] = class_obj

    def fromJson(self, obj, logger=None):
        class_name = obj['__type__']
        obj = self.register[class_name].fromJson(obj, logger=logger)
        return obj

    def fromParam(self, clustering_algo, args, logger=None):
        class_ = self.register[clustering_algo + 'Configuration']
        param = list(inspect.signature(class_.__init__).parameters.keys())
        param.remove('self')
        args['logger'] = logger
        args = {key: args[key] for key in param}
        obj = self.register[clustering_algo + 'Configuration'](**args)
        return obj

    def fromArgs(self, clustering_algo, args, logger=None):
        class_ = self.register[clustering_algo + 'Configuration']
        params = class_.generateParamsFromArgs(args, logger=logger)
        return self.fromParam(clustering_algo, params, logger=logger)

    def generateParser(self, clustering_algo, parser):
        class_ = self.register[clustering_algo + 'Configuration']
        parser = class_.generateParser(parser)
        return parser

    def getAlgorithms(self):
        algos = [k.split('Configuration')[0] for k in self.register.keys()]
        algos.remove('Clustering')
        return algos
