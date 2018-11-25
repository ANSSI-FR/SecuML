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

import abc
from enum import Enum


class exportFieldMethod(Enum):
    primitive = 1
    obj = 2
    string = 3
    obj_class = 4
    enum_value = 5


class Conf(object):

    def __init__(self, logger):
        self.logger = logger

    @abc.abstractmethod
    def fieldsToExport(self):
        return []

    def to_json(self):
        fields = self.fieldsToExport()
        conf = {}
        conf['__type__'] = self.__class__.__name__
        for f, f_type in fields:
            f_value = getattr(self, f)
            if f_type == exportFieldMethod.primitive:
                conf[f] = f_value
            elif f_type == exportFieldMethod.obj:
                if f_value is not None:
                    conf[f] = f_value.to_json()
                else:
                    conf[f] = None
            elif f_type == exportFieldMethod.string:
                conf[f] = str(f_value)
            elif f_type == exportFieldMethod.obj_class:
                if f_value is not None:
                    conf[f] = f_value.__name__
                else:
                    conf[f] = None
            elif f_type == exportFieldMethod.enum_value:
                conf[f] = f_value.name
            else:
                print(f)
                assert(False)
        return conf


class ConfFactory(object):

    def __init__(self):
        self.register = {}

    def registerClass(self, class_name, class_obj):
        self.register[class_name] = class_obj

    def from_json(self, obj, logger):
        class_name = obj['__type__']
        return self.register[class_name].from_json(obj, logger)

    def fromArgs(self, method, args, logger):
        class_ = self.register[method + 'Conf']
        return class_.fromArgs(args, logger)

    def generateParser(self, method_class, parser):
        class_ = self.register[method_class + 'Conf']
        return class_.generateParser(parser)

    def getMethods(self):
        methods = [k.split('Conf')[0] for k in self.register.keys()]
        return methods
