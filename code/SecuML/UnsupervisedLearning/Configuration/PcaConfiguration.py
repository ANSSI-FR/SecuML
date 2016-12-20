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

from SecuML.UnsupervisedLearning.Projection.Pca import Pca
import ProjectionConfFactory
from UnsupervisedProjectionConfiguration import UnsupervisedProjectionConfiguration

class PcaConfiguration(UnsupervisedProjectionConfiguration):

    def __init__(self, num_components = None, sublabels_supervision = None):
        if num_components is None:
            num_components = 20
        UnsupervisedProjectionConfiguration.__init__(self, num_components = num_components,
                sublabels_supervision = sublabels_supervision)
        self.algo = Pca

    @staticmethod
    def fromJson(obj):
        conf = PcaConfiguration(num_components = obj['num_components'], 
                sublabels_supervision = obj['sublabels_supervision'])
        return conf

    def toJson(self):
        conf = UnsupervisedProjectionConfiguration.toJson(self)
        conf['__type__'] = 'PcaConfiguration'
        return conf

ProjectionConfFactory.getFactory().registerClass('PcaConfiguration', 
        PcaConfiguration)
