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
import math


def translate(point, translation):
    [x, y] = point
    [tx, ty] = translation
    [x_trans, y_trans] = [x + tx, y + ty]
    return [x_trans, y_trans]


def scale(point, scaling):
    [x, y] = point
    [sx, sy] = scaling
    [x_scaled, y_scaled] = [x * sx, y * sy]
    return [x_scaled, y_scaled]


class HexagonalBin(object):

    def __init__(self, lattice, size, xmin, ymin, i, j):
        self.lattice = lattice
        self.size = size
        self.xmin = xmin
        self.ymin = ymin
        self.i = i
        self.j = j
        self.malicious_ids = []
        self.ok_ids = []

    def hasInstances(self):
        return len(self.malicious_ids) > 0 or len(self.ok_ids) > 0

    def addData(self, index, malicious_ids):
        if index in malicious_ids:
            self.malicious_ids.append(index)
        else:
            self.ok_ids.append(index)

    def center(self):
        [x_center, y_center] = [0, 0]
        if self.lattice == 1:
            x_center = self.i + 0.5
            y_center = 3 * self.j + 0.5
        else:
            x_center = self.i
            y_center = 3 * self.j + 2
        return [x_center, y_center]

    def hexagon(self):
        hexag = []
        c = self.center()
        nodes = [
            [-0.5,  0.5], [0, 1],
            [0.5, 0.5], [0.5, -0.5],
            [0, -1], [-0.5, -0.5]]
        for node in nodes:
            hexag.append(translate(scale(translate(c, node),
                                         [math.sqrt(3) * self.size, self.size]),
                                   [self.xmin, self.ymin]))
        return hexag

    def toJson(self):
        json = {}
        json['hexagon'] = self.hexagon()
        json['center'] = translate(scale(self.center(),
                                         [math.sqrt(3) * self.size, self.size]),
                                   [self.xmin, self.ymin])
        json['num_malicious_instances'] = len(self.malicious_ids)
        json['num_ok_instances'] = len(self.ok_ids)
        json['malicious_instances'] = self.malicious_ids
        json['ok_instances'] = self.ok_ids
        json['prop_malicious'] = \
            len(self.malicious_ids) / \
            (len(self.malicious_ids) + len(self.ok_ids))
        return json


class HexagonalBinEncoder(json.JSONEncoder):
    def default(self, obj):
        if getattr(obj, 'toJson', None):
            return obj.toJson()
