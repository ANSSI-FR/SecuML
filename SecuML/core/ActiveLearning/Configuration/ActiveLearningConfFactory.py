# SecuML
# Copyright (C) 2016-2017  ANSSI
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

active_learning_conf_factory = None


def getFactory():
    global active_learning_conf_factory
    if active_learning_conf_factory is None:
        active_learning_conf_factory = ActiveLearningConfFactory()
    return active_learning_conf_factory


class ActiveLearningConfFactory(object):

    def __init__(self):
        self.register = {}

    def registerClass(self, class_name, class_obj):
        self.register[class_name] = class_obj

    def fromJson(self, obj):
        class_name = obj['__type__']
        obj = self.register[class_name].fromJson(obj)
        return obj

    def fromParam(self, query_strategy, args, logger=None):
        class_ = self.register[query_strategy + 'Configuration']
        param = list(inspect.signature(class_.__init__).parameters.keys())
        param.remove('self')
        args['logger'] = logger
        args = {key: args[key] for key in param}
        obj = self.register[query_strategy + 'Configuration'](**args)
        return obj

    def fromArgs(self, query_strategy, args, logger=None):
        class_ = self.register[query_strategy + 'Configuration']
        params = class_.generateParamsFromArgs(args, logger=logger)
        return self.fromParam(query_strategy, params, logger=logger)

    def generateParser(self, query_strategy, parser):
        class_ = self.register[query_strategy + 'Configuration']
        parser = class_.generateParser(parser)
        return parser

    def getStrategies(self):
        strategies = [k.split('Configuration')[0] for k in self.register.keys()]
        return strategies
