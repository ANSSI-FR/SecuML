# SecuML
# Copyright (C) 2016  ANSSI
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

from SecuML.core.DimensionReduction.Algorithms.Projection.Pca import Pca
from SecuML.core.DimensionReduction.Configuration \
        import DimensionReductionConfFactory

from .UnsupervisedProjectionConfiguration \
        import UnsupervisedProjectionConfiguration


class PcaConfiguration(UnsupervisedProjectionConfiguration):

    def __init__(self, num_components=None, logger=None):
        UnsupervisedProjectionConfiguration.__init__(
                        self,
                        Pca,
                        num_components=num_components,
                        logger=logger)
        if self.num_components is None:
            self.num_components = 20

    @staticmethod
    def fromJson(obj, logger=None):
        conf = PcaConfiguration(num_components=obj['num_components'],
                                logger=logger)
        return conf

    def toJson(self):
        conf = UnsupervisedProjectionConfiguration.toJson(self)
        conf['__type__'] = 'PcaConfiguration'
        return conf


DimensionReductionConfFactory.getFactory().registerClass('PcaConfiguration',
                                                         PcaConfiguration)
