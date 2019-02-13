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
import importlib
import pkgutil


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
    def fields_to_export(self):
        return []

    def to_json(self):
        fields = self.fields_to_export()
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
        self.methods = {}

    def register(self, class_name, class_obj):
        self.methods[class_name] = class_obj

    def from_json(self, obj, logger):
        return self.methods[obj['__type__']].from_json(obj, logger)

    def from_args(self, method, args, logger):
        return self.get_class(method).from_args(args, logger)

    def gen_parser(self, method, parser):
        return self.get_class(method).gen_parser(parser)

    def get_class(self, method):
        return self.methods[method + 'Conf']

    def get_methods(self):
        return [k.split('Conf')[0] for k in self.methods.keys()]


def register_submodules(module, factory):
    for _, name, _ in pkgutil.iter_modules(module.__path__):
        class_name = '%sConf' % ''.join(map(lambda x: x.capitalize(),
                                        name.split('_')))
        submodule = importlib.import_module(module.__name__ + '.' + name)
        factory.register(class_name, getattr(submodule, class_name))
