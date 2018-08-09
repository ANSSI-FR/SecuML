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

from SecuML.core.DimensionReduction.Algorithms.Projection.Sdml import Sdml
from SecuML.core.DimensionReduction.Configuration import DimensionReductionConfFactory

from .SemiSupervisedProjectionConfiguration import SemiSupervisedProjectionConfiguration


class SdmlConfiguration(SemiSupervisedProjectionConfiguration):

    def __init__(self, families_supervision=None):
        SemiSupervisedProjectionConfiguration.__init__(
            self, Sdml, families_supervision=families_supervision)

    @staticmethod
    def fromJson(obj):
        conf = SdmlConfiguration(
            families_supervision=obj['families_supervision'])
        conf.num_components = obj['num_components']
        return conf

    def toJson(self):
        conf = SemiSupervisedProjectionConfiguration.toJson(self)
        conf['__type__'] = 'SdmlConfiguration'
        return conf


DimensionReductionConfFactory.getFactory().registerClass('SdmlConfiguration',
                                                         SdmlConfiguration)
