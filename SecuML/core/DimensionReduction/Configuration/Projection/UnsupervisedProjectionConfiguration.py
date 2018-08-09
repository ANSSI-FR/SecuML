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

from SecuML.core.DimensionReduction.Configuration.DimensionReductionConfiguration \
    import DimensionReductionConfiguration


class UnsupervisedProjectionConfiguration(DimensionReductionConfiguration):

    def __init__(self, algo, num_components=None):
        DimensionReductionConfiguration.__init__(self, algo)
        self.num_components = num_components

    def toJson(self):
        conf = DimensionReductionConfiguration.toJson(self)
        conf['__type__'] = 'UnsupervisedProjection.Configuration'
        conf['num_components'] = self.num_components
        return conf

    @staticmethod
    def generateParamsFromArgs(args):
        params = DimensionReductionConfiguration.generateParamsFromArgs(args)
        params['num_components'] = args.num_components
        return params

    @staticmethod
    def generateParser(parser):
        parser.add_argument('--num-components',
                            type=int,
                            default=None)
