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

import numpy as np
from secuml.core.tools.color import get_label_color


class PlotDataset(object):

    def __init__(self, values, label):
        self.values = np.asanyarray(values)
        self.label = label
        self._set_default_values()

    def add_error_bars(self, errors):
        self.error_bars = errors

    def set_color(self, color):
        self.color = color

    def set_linewidth(self, linewidth):
        self.linewidth = linewidth

    def set_linestyle(self, linestyle):
        self.linestyle = linestyle

    def set_marker(self, marker):
        self.marker = marker

    def _set_default_values(self):
        self.color = get_label_color('all')
        self.linewidth = 3
        self.linestyle = 'solid'
        self.marker = 'o'
        self.error_bars = None
