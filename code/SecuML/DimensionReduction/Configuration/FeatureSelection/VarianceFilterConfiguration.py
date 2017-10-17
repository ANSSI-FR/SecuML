## SecuML
## Copyright (C) 2017  ANSSI
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

from SecuML.DimensionReduction.Algorithms.FeatureSelection.VarianceFilter import VarianceFilter
from SecuML.DimensionReduction.Configuration import DimensionReductionConfFactory

from UnsupervisedFeatureSelectionConfiguration import UnsupervisedFeatureSelectionConfiguration

class VarianceFilterConfiguration(UnsupervisedFeatureSelectionConfiguration):

    def __init__(self):
        UnsupervisedFeatureSelectionConfiguration.__init__(self, VarianceFilter)

    @staticmethod
    def fromJson(obj):
        conf = VarianceFilterConfiguration()
        return conf

    def toJson(self):
        conf = UnsupervisedFeatureSelectionConfiguration.toJson(self)
        conf['__type__'] = 'VarianceFilterConfiguration'
        return conf

DimensionReductionConfFactory.getFactory().registerClass('VarianceFilterConfiguration',
                                                         VarianceFilterConfiguration)
