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

import math
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KernelDensity


class Density(object):

    def __init__(self, num_points, bandwidth, title=None):
        self.num_points = num_points
        self.bandwidth = bandwidth
        self.title = title
        self.datasets = []

    def addDataset(self, dataset):
        self.datasets.append(dataset)

    def display(self, output_filename):
        fig, (self.ax) = plt.subplots(1, 1)
        self.kde = KernelDensity(kernel='gaussian', bandwidth=self.bandwidth)
        for i in range(len(self.datasets)):
            self.displayDataset(self.datasets[i])
        if self.title is not None:
            self.ax.set_xlabel(self.title)
        self.ax.set_ylabel('Density')
        self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                       ncol=3, mode='expand', borderaxespad=0.)
        fig.savefig(output_filename)
        plt.close(fig)

    def displayDataset(self, dataset):
        eps = 0.00001
        linewidth = dataset.linewidth
        if np.var(dataset.values) < eps:
            linewidth += 2
            mean = np.mean(dataset.values)
            x = np.arange(0, 1, 0.1)
            x = np.sort(np.append(x, [mean, mean - eps, mean + eps]))
            density = [1 if v == mean else 0 for v in x]
        else:
            self.kde.fit(np.asarray([[x] for x in dataset.values]))
            # Computes the x axis
            x_max = np.amax(dataset.values)
            x_min = np.amin(dataset.values)
            delta = x_max - x_min
            density_delta = 1.1 * delta
            x = np.arange(x_min, x_max, density_delta / self.num_points)
            x_density = [[y] for y in x]
            # kde.score_samples returns the 'log' of the density
            log_density = self.kde.score_samples(x_density).tolist()
            density = list(map(math.exp, log_density))
        self.ax.plot(x, density, label=dataset.label, color=dataset.color,
                     linewidth=linewidth, linestyle=dataset.linestyle)
