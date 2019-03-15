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
from secuml.core.conf import exportFieldMethod


class ProjectionConf(Conf):

    def __init__(self, logger, num_components):
        Conf.__init__(self, logger)
        self.num_components = num_components
        self._set_algo()

    @abc.abstractmethod
    def _get_algo(self):
        return

    def _set_algo(self):
        self.algo = self._get_algo()
        self.algo_name = self.algo.__name__

    def get_exp_name(self):
        return self.algo.__name__

    def fields_to_export(self):
        return [('algo', exportFieldMethod.obj_class),
                ('num_components', exportFieldMethod.primitive)]

    @staticmethod
    def gen_parser(parser):
        parser.add_argument('--num-components',
                            type=int,
                            default=None)


class UnsupervisedProjectionConf(ProjectionConf):

    pass


class SemiSupervisedProjectionConf(ProjectionConf):

    def __init__(self, logger, num_components=None, multiclass=None):
        ProjectionConf.__init__(self, logger, num_components)
        self.multiclass = multiclass

    def get_exp_name(self):
        suffix = ProjectionConf.get_exp_name(self)
        if self.multiclass:
            suffix += '__multiclass'
        return suffix

    def fields_to_export(self):
        fields = ProjectionConf.fields_to_export(self)
        fields.extend([('multiclass', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def gen_parser(parser):
        ProjectionConf.gen_parser(parser)
        parser.add_argument(
                 '--multiclass',
                 action='store_true',
                 default=False,
                 help='When set to True, the semi-supervision is based on the '
                      'families instead of the binary labels. ')


projection_conf_factory = None


def get_factory():
    global projection_conf_factory
    if projection_conf_factory is None:
        projection_conf_factory = ProjectionConfFactory()
    return projection_conf_factory


class ProjectionConfFactory(ConfFactory):
    pass
