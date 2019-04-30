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

import math
import numpy as np
from scipy.sparse.base import spmatrix

from secuml.core.tools.color import get_label_color


class PlotDataset(object):

    def __init__(self, values, label, xvalues=None, error_bars=None):
        self._set_values(values)
        self.label = label
        self.xvalues = xvalues
        self.error_bars = error_bars
        self._set_default_values()

    def _set_values(self, values):
        self.values = values
        if len(self.values.shape) == 1:
            new_shape = (self.values.shape[0], 1)
            if isinstance(self.values, spmatrix):
                self.values = self.values.reshape(new_shape)
            else:
                self.values = np.reshape(self.values, new_shape)

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


class ErrorPlotDataset(PlotDataset):

    def __init__(self, values_lists, label, xvalues=None):
        values_matrix = values_lists
        values = self._compute_values(values_matrix)
        error_bars = self._compute_error_bars(values_matrix)
        PlotDataset.__init__(self, values, label, xvalues=xvalues,
                             error_bars=error_bars)

    def _compute_values(self, values_matrix):
        return np.mean(values_matrix, axis=0)

    # 95% confidence interval.
    def _compute_error_bars(self, values_matrix):
        std = np.std(values_matrix, axis=0)
        return 1.96 * std / math.sqrt(values_matrix.shape[0])
