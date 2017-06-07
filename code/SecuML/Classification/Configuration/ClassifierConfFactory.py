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

import inspect

classifier_conf_factory = None

def getFactory():
    global classifier_conf_factory
    if classifier_conf_factory is None:
        classifier_conf_factory = ClassifierConfFactory()
    return classifier_conf_factory

class ClassifierConfFactory(object):

    def __init__(self):
        self.register = {}

    def registerClass(self, class_name, class_obj):
        self.register[class_name] = class_obj

    def fromJson(self, obj, exp):
        class_name = obj['__type__']
        obj = self.register[class_name].fromJson(obj, exp)
        return obj

    def fromParam(self, class_name, args):
        class_ = self.register[class_name + 'Configuration']
        param = inspect.getargspec(class_.__init__).args
        param.remove('self')
        args = [args[key] for key in param]
        obj = class_(*args)
        return obj

    def fromArgs(self, model, args, experiment):
        class_ = self.register[model + 'Configuration']
        params = class_.generateParamsFromArgs(args, experiment)
        return self.fromParam(model, params)

    def generateParser(self, labeling_strategy, parser):
        class_ = self.register[labeling_strategy + 'Configuration']
        return class_.generateParser(parser)
