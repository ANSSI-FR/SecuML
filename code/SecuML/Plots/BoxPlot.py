## SecuML
## Copyright (C) 2016  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

class BoxPlot(object):

    def __init__(self, title = None):
        self.title    = title
        self.datasets = []

    def addDataset(self, dataset):
        self.datasets.append(dataset)

    def display(self, output_filename):
        fig, (ax) = plt.subplots(1, 1)
        data   = [d.values for d in self.datasets]
        labels = [d.label for d in self.datasets]
        bp = ax.boxplot(data, labels = labels, notch = 0, sym = '+', vert = '1', whis = 1.5)
        plt.setp(bp['boxes'], color='black')
        plt.setp(bp['whiskers'], color='black')
        plt.setp(bp['fliers'], color='black', marker='+')
        for i in range(len(self.datasets)):
            box = bp['boxes'][i]
            box_x = []
            box_y = []
            for j in range(5):
                box_x.append(box.get_xdata()[j])
                box_y.append(box.get_ydata()[j])
            box_coords = list(zip(box_x, box_y))
            box_polygon = Polygon(box_coords, facecolor = self.datasets[i].color)
            ax.add_patch(box_polygon)
        if self.title is not None:
            ax.set_title(self.title)
        x_min = np.amin([np.amin(d.values) for d in self.datasets])
        x_max = np.amax([np.amax(d.values) for d in self.datasets])
        ax.set_ylim(x_min - 0.05*(x_max - x_min), x_max + 0.05*(x_max - x_min))
        fig.savefig(output_filename)
        plt.close(fig)
