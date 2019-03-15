# SecuML
# Copyright (C) 2016-2019  ANSSI
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

from secuml.core.conf import Conf
from secuml.core.conf import ConfFactory


objective_func_conf_factory = None


def get_factory():
    global objective_func_conf_factory
    if objective_func_conf_factory is None:
        objective_func_conf_factory = ObjectiveFuncConfFactory()
    return objective_func_conf_factory


class ObjectiveFuncConfFactory(ConfFactory):
    pass


class ObjectiveFuncConf(Conf):

    @abc.abstractmethod
    def get_scoring_method(self):
        return

    @staticmethod
    def gen_parser(parser):
        factory = get_factory()
        methods = factory.get_methods()
        parser.add_argument('--objective-func',
                            choices=methods,
                            default='RocAuc',
                            help='Default: RocAuc. ')
        for method in methods:
            factory.gen_parser(method, parser)
