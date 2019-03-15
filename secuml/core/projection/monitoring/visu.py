# SecuML
# Copyright (C) 2016-2019  ANSSI
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

from secuml.core.data.labels_tools import MALICIOUS
from secuml.core.tools.plots.hexagonal_binning import HexagonalBinning


class Visualization(object):

    def __init__(self, projection, output_dir):
        self.projection = projection
        self.output_dir = output_dir

    def all_hex_bin(self, instances):
        malicious_ids = instances.annotations.get_annotated_ids(MALICIOUS)
        num_components = instances.features.num_features()
        num_components = min(num_components, 10)
        for i in range(num_components - 1):
            for j in range(i + 1, num_components):
                self.one_hex_bin(instances, i, j, malicious_ids)

    # Algorithm from 'Scatterplot matrix techniques for large N'
    # by Carr, Littlefield, Nicholson, and Littlefield
    def one_hex_bin(self, instances, cx_index, cy_index, malicious_ids):
        x = instances.features.get_values_from_index(cx_index)
        y = instances.features.get_values_from_index(cy_index)
        hex_bin = HexagonalBinning(x, y, instances.ids.get_ids(), 30,
                                   malicious_ids)
        hex_bin.compute_binning()
        filename = 'c_%d_%d_hexbin.json' % (cx_index, cy_index)
        output_file = path.join(self.output_dir, filename)
        hex_bin.print_binning(cx_index, cy_index, output_file)
