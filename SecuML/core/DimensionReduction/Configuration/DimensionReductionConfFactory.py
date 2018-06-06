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

projection_conf_factory = None


def getFactory():
    global projection_conf_factory
    if projection_conf_factory is None:
        projection_conf_factory = DimensionReductionConfFactory()
    return projection_conf_factory


class DimensionReductionConfFactory(object):

    def __init__(self):
        self.register = {}

    def registerClass(self, class_name, class_obj):
        self.register[class_name] = class_obj

    def fromJson(self, obj):
        class_name = obj['__type__']
        obj = self.register[class_name].fromJson(obj)
        return obj

    def fromParam(self, projection_algo, args, logger=None):
        class_ = self.register[projection_algo + 'Configuration']
        param = list(inspect.signature(class_.__init__).parameters.keys())
        param.remove('self')
        args['logger'] = logger
        args = [args[key] for key in param]
        obj = class_(*args)
        return obj

    def fromArgs(self, algo, args, logger=None):
        class_ = self.register[algo + 'Configuration']
        params = class_.generateParamsFromArgs(args)
        return self.fromParam(algo, params, logger=logger)

    def generateParser(self, labeling_strategy, parser):
        class_ = self.register[labeling_strategy + 'Configuration']
        return class_.generateParser(parser)
