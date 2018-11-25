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

from SecuML.core.Conf import exportFieldMethod
from .ProjectionConf import ProjectionConf


class SemiSupervisedProjectionConf(ProjectionConf):

    def __init__(self, logger, algo, num_components=None,
            families_supervision=None):
        ProjectionConf.__init__(self, algo, logger)
        self.families_supervision = families_supervision
        self.num_components = num_components

    def get_exp_name(self):
        suffix = ProjectionConf.get_exp_name(self)
        if self.families_supervision:
            suffix += '__familiesSupervision'
        return suffix

    def fieldsToExport(self):
        fields = ProjectionConf.fieldsToExport(self)
        fields.extend([('num_components', exportFieldMethod.primitive),
                       ('families_supervision', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def generateParser(parser):
        ProjectionConf.generateParser(parser)
        parser.add_argument('--num-components',
                            type=int,
                            default=None)
        parser.add_argument('--families-supervision',
                 action='store_true',
                 default=False,
                 help='When set to True, the semi-supervision is based on the '
                      'families instead of the binary labels. ')
