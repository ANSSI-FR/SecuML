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

from SecuML.core.projection.algos.Itml import Itml
from SecuML.core.projection.conf import ProjectionConfFactory

from .SemiSupervisedProjectionConf import SemiSupervisedProjectionConf


class ItmlConf(SemiSupervisedProjectionConf):

    def __init__(self, logger, families_supervision=None):
        SemiSupervisedProjectionConf.__init__(self, logger, Itml,
                                    families_supervision=families_supervision)

    @staticmethod
    def from_json(obj, logger):
        conf = ItmlConf(logger,
                        families_supervision=obj['families_supervision'])
        conf.num_components = obj['num_components']
        return conf

    @staticmethod
    def fromArgs(args, logger):
        return ItmlConf(logger, args.families_supervision)


ProjectionConfFactory.getFactory().registerClass('ItmlConf', ItmlConf)
