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

from SecuML.DimensionReduction.Configuration.DimensionReductionConfiguration \
        import DimensionReductionConfiguration

class UnsupervisedFeatureSelectionConfiguration(DimensionReductionConfiguration):

    def __init__(self, algo):
        DimensionReductionConfiguration.__init__(self, algo)

    def generateSuffix(self):
        suffix = DimensionReductionConfiguration.generateSuffix(self)
        return suffix

    def toJson(self):
        conf = DimensionReductionConfiguration.toJson(self)
        conf['__type__'] = 'UnsupervisedFeatureSelection.Configuration'
        return conf
