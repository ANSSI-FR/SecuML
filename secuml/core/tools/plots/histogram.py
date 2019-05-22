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

import numpy as np

from .barplot import BarPlot
from .dataset import PlotDataset


class Histogram(BarPlot):

    def __init__(self, datasets, logger, num_bins=10, title=None, xlabel=None,
                 ylabel=None):
        self.logger = logger
        bin_edges = self._get_bin_edges(datasets, num_bins)
        x_labels = ['%.2f - %.2f' % (bin_edges[e], bin_edges[e+1])
                    for e in range(len(bin_edges) - 1)]
        BarPlot.__init__(self, x_labels, title=title, xlabel=xlabel,
                         ylabel=ylabel)
        for label, dataset in datasets.items():
            if dataset.values.shape[0] > 0:
                hist, _ = np.histogram(dataset.values, bins=bin_edges,
                                       density=False)
                hist_dataset = PlotDataset(hist, label)
                hist_dataset.set_color(dataset.color)
                BarPlot.add_dataset(self, hist_dataset)

    def _get_bin_edges(self, datasets, num_bins):
        all_values = None
        for kind, dataset in datasets.items():
            if all_values is None:
                all_values = dataset.values
            else:
                all_values = np.vstack((all_values, dataset.values))
        # Added to deal with numpy issue #8627.
        # When the minimum and the maximum values are equal and
        # the maximum value is greater than 2**53,
        # the values are caped to 2**53  - 1.
        if all_values.min() == all_values.max() and all_values.max() >= 2**53:
            np.clip(all_values, None, 2**53-1, out=all_values)
            self.logger.warning('The values of the histogram have been caped '
                                'to 2**53-1 to deal with numpy issue #8627. ')
        _, bin_edges = np.histogram(all_values, bins=num_bins, density=False)
        return bin_edges
