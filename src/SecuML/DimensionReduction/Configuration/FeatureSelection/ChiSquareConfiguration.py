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

from SecuML.DimensionReduction.Algorithms.FeatureSelection.ChiSquare import ChiSquare
from SecuML.DimensionReduction.Configuration import DimensionReductionConfFactory

from SemiSupervisedFeatureSelectionConfiguration import SemiSupervisedFeatureSelectionConfiguration

class ChiSquareConfiguration(SemiSupervisedFeatureSelectionConfiguration):

    def __init__(self, num_components = None, families_supervision = None):
        SemiSupervisedFeatureSelectionConfiguration.__init__(self, ChiSquare,
                num_components = num_components,
                families_supervision = families_supervision)

    @staticmethod
    def fromJson(obj):
        conf = ChiSquareConfiguration(num_components = obj['num_components'],
                families_supervision = obj['families_supervision'])
        return conf

    def toJson(self):
        conf = SemiSupervisedFeatureSelectionConfiguration.toJson(self)
        conf['__type__'] = 'ChiSquareConfiguration'
        return conf

DimensionReductionConfFactory.getFactory().registerClass('ChiSquareConfiguration',
                                                         ChiSquareConfiguration)
