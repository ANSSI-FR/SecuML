## SecuML
## Copyright (C) 2016-2017  ANSSI
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

import inspect

active_learning_conf_factory = None

def getFactory():
    global active_learning_conf_factory
    if active_learning_conf_factory is None:
        active_learning_conf_factory = ActiveLearningConfFactory()
    return active_learning_conf_factory

class ActiveLearningConfFactory():

    def __init__(self):
        self.register = {}

    def registerClass(self, class_name, class_obj):
        self.register[class_name] = class_obj

    def fromJson(self, obj, experiment):
        class_name = obj['__type__']
        obj = self.register[class_name].fromJson(obj, experiment)
        return obj

    def fromParam(self, labeling_strategy, args):
        class_ = self.register[labeling_strategy + 'Configuration']
        param = inspect.getargspec(class_.__init__).args
        param.remove('self')
        args = {key: args[key] for key in param}
        obj = self.register[labeling_strategy + 'Configuration'](**args)
        return obj

    def fromArgs(self, labeling_strategy, args, experiment):
        class_ = self.register[labeling_strategy + 'Configuration']
        params = class_.generateParamsFromArgs(args, experiment)
        return self.fromParam(labeling_strategy, params)

    def generateParser(self, labeling_strategy, parser):
        class_ = self.register[labeling_strategy + 'Configuration']
        parser = class_.generateParser(parser)
        return parser

    def checkInputParams(self, args, session):
        class_ = self.register[args.strategy + 'Configuration']
        class_.checkInputParams(args, session)
