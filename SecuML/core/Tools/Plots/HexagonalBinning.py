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

import json
import numpy as np
import math
import matplotlib.transforms as mtrans

from .HexagonalBin import HexagonalBin, HexagonalBinEncoder

epsilon = 0.001


class HexagonalBinning(object):

    def __init__(self, x, y, ids, nx, malicious_ids):

        self.malicious_ids = malicious_ids

        self.x = np.array(x, float)
        self.y = np.array(y, float)
        self.ids = ids

        self.xmin = np.amin(x)
        self.xmax = np.amax(x)
        self.ymin = np.amin(y)
        self.ymax = np.amax(y)

        # to avoid issues with singular data, expand the min/max pairs
        self.xmin, self.xmax = mtrans.nonsingular(
            self.xmin,
            self.xmax,
            expander=0.1)
        self.ymin, self.ymax = mtrans.nonsingular(
            self.ymin,
            self.ymax,
            expander=0.1)

        # In the x-direction, the hexagons exactly cover the region from
        # xmin to xmax. Need some padding to avoid roundoff errors.
        padding = 1.e-9 * (self.xmax - self.xmin)
        self.xmin -= padding
        self.xmax += padding

        # Deal with very small values
        if self.xmax - self.xmin < epsilon:
            self.xmin -= epsilon / 2
            self.xmax += epsilon / 2
        if self.ymax - self.ymin < epsilon:
            self.ymin -= epsilon / 2
            self.ymax += epsilon / 2

        self.nx = nx
        self.size = (self.xmax - self.xmin) / self.nx
        self.nx = int(math.ceil((self.xmax - self.xmin) /
                                (math.sqrt(3) * self.size))) + 1
        self.ny = int(math.ceil((self.ymax - self.ymin) /
                                self.size)) + 1

        self.x_scale = (self.x - self.xmin) / (self.size * math.sqrt(3))
        self.y_scale = (self.y - self.ymin) / self.size

    def computeBinning(self):

        # Looks for the closest hexagon center in each grid
        i_1 = np.round(self.x_scale - 0.5).astype(int)
        j_1 = np.round((self.y_scale - 0.5) / 3).astype(int)
        i_2 = np.round(self.x_scale).astype(int)
        j_2 = np.round((self.y_scale - 2) / 3).astype(int)

        x_1 = i_1 + 0.5
        y_1 = 3 * j_1 + 0.5
        x_2 = i_2
        y_2 = 3 * j_2 + 2

        # Finds the closest hexagon among the two grids
        d1 = 3 * (self.x_scale - x_1) ** 2 + (self.y_scale - y_1) ** 2
        d2 = 3 * (self.x_scale - x_2) ** 2 + (self.y_scale - y_2) ** 2
        bdist = (d1 < d2)

        self.lattice1 = np.empty((self.nx, self.ny), dtype=object)
        self.lattice2 = np.empty((self.nx, self.ny), dtype=object)
        for i in range(self.nx):
            for j in range(self.ny):
                self.lattice1[i, j] = HexagonalBin(1, self.size,
                                                   self.xmin, self.ymin, i, j)
                self.lattice2[i, j] = HexagonalBin(2, self.size,
                                                   self.xmin, self.ymin, i, j)
        for i in range(len(self.x)):
            if bdist[i]:
                self.lattice1[i_1[i], j_1[i]].addData(
                    self.ids[i], self.malicious_ids)
            else:
                self.lattice2[i_2[i], j_2[i]].addData(
                    self.ids[i], self.malicious_ids)

    def printBinning(self, pc_x_index, pc_y_index, output_file):
        with open(output_file, 'w') as f:
            k = 0
            f.write('[')

            # Prints xmin, xmax, ymin, ymax
            line = '{'
            line += '"xmin":' + str(self.xmin) + ','
            line += '"xmax":' + str(self.xmax) + ','
            line += '"ymin":' + str(self.ymin) + ','
            line += '"ymax":' + str(self.ymax)
            line += '},'
            f.write(line)

            # Prints information about each hexagonal bin
            for i in range(self.nx):
                for j in range(self.ny):
                    if self.lattice1[i, j].hasInstances():
                        if k != 0:
                            f.write(',')
                        json.dump(self.lattice1[i, j], f, cls=HexagonalBinEncoder,
                                  sort_keys=True)
                        k += 1
                    if self.lattice2[i, j].hasInstances():
                        if k != 0:
                            f.write(',')
                        json.dump(self.lattice2[i, j], f, cls=HexagonalBinEncoder,
                                  sort_keys=True)
                        k += 1
            f.write('\n]')
