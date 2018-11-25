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

from SecuML.core.projection.algos.Rca import Rca
from SecuML.core.projection.conf import ProjectionConfFactory

from .SemiSupervisedProjectionConf import SemiSupervisedProjectionConf


class RcaConf(SemiSupervisedProjectionConf):

    def __init__(self, logger, num_components=None, families_supervision=None):
        SemiSupervisedProjectionConf.__init__(self, logger, Rca,
                                    num_components=num_components,
                                    families_supervision=families_supervision)

    @staticmethod
    def from_json(obj, logger):
        return RcaConf(logger, num_components=obj['num_components'],
                       families_supervision=obj['families_supervision'])

    @staticmethod
    def fromArgs(args, logger):
        return RcaConf(logger, num_components=args.num_components,
                       families_supervision=args.families_supervision)


ProjectionConfFactory.getFactory().registerClass('RcaConf', RcaConf)
