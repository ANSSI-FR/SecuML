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
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KernelDensity


class Density(object):

    def __init__(self, num_points=200, bandwidth=0.3, title=None,
                 min_value=None, max_value=None):
        self.num_points = num_points
        self.bandwidth = bandwidth
        self.title = title
        self.datasets = []
        self.min_value = min_value
        self.max_value = max_value

    def add_dataset(self, dataset):
        self.datasets.append(dataset)
        min_value = np.amin(dataset.values)
        max_value = np.amax(dataset.values)
        if self.min_value is None:
            self.min_value = min_value
        else:
            self.min_value = min(self.min_value, min_value)
        if self.max_value is None:
            self.max_value = max_value
        else:
            self.max_value = max(self.max_value, max_value)

    def display(self, output_filename):
        fig, (self.ax) = plt.subplots(1, 1)
        self.kde = KernelDensity(kernel='gaussian', bandwidth=self.bandwidth)
        has_legend = False
        for dataset in self.datasets:
            self._display_dataset(dataset)
            if dataset.label is not None:
                has_legend = True
        if self.title is not None:
            self.ax.set_xlabel(self.title)
        self.ax.set_ylabel('Density')
        if has_legend:
            self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3,
                           mode='expand', borderaxespad=0.)
        fig.savefig(output_filename)
        plt.close(fig)

    def _display_dataset(self, dataset):
        eps = 0.00001
        linewidth = dataset.linewidth
        delta = self.max_value - self.min_value
        density_delta = 1.2 * delta
        if delta > 0:
            x = np.arange(self.min_value - 0.1*delta,
                          self.max_value + 0.1*delta,
                          density_delta / self.num_points)
        else:
            x = np.array([self.min_value - 2*eps, self.max_value + 2*eps])
        if np.var(dataset.values) < eps:
            linewidth += 2
            mean = np.mean(dataset.values)
            x = np.sort(np.append(x, [mean, mean - eps, mean + eps]))
            density = [1 if v == mean else 0 for v in x]
        else:
            self.kde.fit(np.asarray([[x] for x in dataset.values]))
            x_density = [[y] for y in x]
            # kde.score_samples returns the 'log' of the density
            log_density = self.kde.score_samples(x_density).tolist()
            density = list(map(math.exp, log_density))
        self.ax.plot(x, density, label=dataset.label, color=dataset.color,
                     linewidth=linewidth, linestyle=dataset.linestyle)
