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

import os.path as path

from SecuML.core.Data import labels_tools
from SecuML.core.Tools.Plots.HexagonalBinning import HexagonalBinning


class Visualization(object):

    def __init__(self, projection, output_directory):
        self.projection = projection
        self.output_directory = output_directory

    def allHexBin(self, projected_instances):
        malicious_ids = projected_instances.annotations.getAnnotatedIds(
            labels_tools.MALICIOUS)
        num_components = projected_instances.features.numFeatures()
        num_components = min(num_components, 10)
        for i in range(num_components - 1):
            for j in range(i + 1, num_components):
                self.oneHexBin(projected_instances, i, j, malicious_ids)

    # Algorithm from 'Scatterplot matrix techniques for large N'
    # by Carr, Littlefield, Nicholson, and Littlefield
    def oneHexBin(self, projected_instances, cx_index, cy_index,
                  malicious_ids):
        x = projected_instances.features.getFeatureValuesFromIndex(cx_index)
        y = projected_instances.features.getFeatureValuesFromIndex(cy_index)
        hex_bin = HexagonalBinning(x, y,
                                   projected_instances.ids.getIds(), 30, malicious_ids)
        hex_bin.computeBinning()
        filename = 'c_' + str(cx_index) + '_' + str(cy_index) + '_hexbin'
        filename += '.json'
        output_file = path.join(self.output_directory, filename)
        hex_bin.printBinning(cx_index, cy_index, output_file)
