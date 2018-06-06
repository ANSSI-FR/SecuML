# SecuML
# Copyright (C) 2016-2017  ANSSI
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
import matplotlib.pyplot as plt
import json


class BarPlot(object):

    def __init__(self, labels, title=None, xlabel=None, ylabel=None):
        self.labels = labels
        self.datasets = []
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

    def addDataset(self, dataset):
        self.datasets.append(dataset)

    def toJson(self, tooltip_data=None):
        json_barplot = {}
        json_barplot['labels'] = self.labels
        json_barplot['datasets'] = []
        if tooltip_data is not None:
            json_barplot['tooltip_data'] = tooltip_data
        for i, dataset in enumerate(self.datasets):
            json_dataset = {}
            json_dataset['data'] = list(map(str, dataset.values))
            json_dataset['backgroundColor'] = dataset.color
            json_dataset['label'] = dataset.label
            json_barplot['datasets'].append(json_dataset)
        return json_barplot

    def exportJson(self, f, tooltip_data=None):
        json_barplot = self.toJson(tooltip_data=tooltip_data)
        json.dump(json_barplot, f, indent=2)

    def toPng(self, filename, bar_width=0.3):
        plt.clf()
        n_groups = len(self.labels)
        index = np.arange(n_groups)
        num_datasets = len(self.datasets)
        for i in range(num_datasets):
            dataset = self.datasets[i]
            if dataset.error_bars is not None:
                plt.bar(index + i * bar_width,
                        dataset.values,
                        bar_width,
                        color=dataset.color,
                        label=dataset.label,
                        yerr=dataset.error_bars)
            else:
                plt.bar(index + i * bar_width,
                        dataset.values,
                        bar_width,
                        color=dataset.color,
                        label=dataset.label)
        if self.xlabel is not None:
            plt.xlabel(self.xlabel)
        if self.ylabel is not None:
            plt.ylabel(self.ylabel)
        if self.title is not None:
            plt.title(self.title)
        plt.xticks(index + bar_width * float(n_groups) / 2., self.labels)
        plt.legend(loc='upper left')
        plt.savefig(filename)
        plt.clf()

    def toPgfPlot(self, filename):
        with open(filename, 'w') as f:
            f.write('\\begin{tikzpicture}' + '\n')
            f.write('\t\\begin{axis} [' + '\n')
            f.write('\t\tybar,' + '\n')
            f.write('\t\tbar width = 7pt,' + '\n')
            f.write('\t\tenlarge y limits = {0.25, upper},' + '\n')
            f.write('\t\tenlarge x limits = 0.25,' + '\n')
            f.write('\t\tsymbolic x coords={' +
                    ','.join(self.labels) + '},' + '\n')

            f.write('\t\tx tick label style={rotate=45, anchor=east},' + '\n')
            if self.xlabel is not None:
                f.write('\t\txlabel=\large ' + self.xlabel + ',' + '\n')
            if self.ylabel is not None:
                f.write('\t\tylabel=\large ' + self.ylabel + ',' + '\n')
            if self.title is not None:
                f.write('\t\ttitle = ' + self.title + ',' + '\n')
            f.write('\t\tymin = 0.0,' + '\n')
            f.write('\t\txlabel near ticks,' + '\n')
            f.write('\t\tylabel near ticks,' + '\n')
            f.write('\t\tlegend pos = north west,' + '\n')
            f.write('\t\tlegend cell align = left' + '\n')
            f.write('\t]' + '\n')

            legend = []
            for i, dataset in enumerate(self.datasets):
                if dataset.error_bars is None:
                    f.write('\t\\addplot[fill=' + dataset.color +
                            ', color=' + dataset.color + '] coordinates {' + '\n')
                    for l, label in enumerate(self.labels):
                        f.write('\t\t(' + label + ',' +
                                str(dataset.values[l]) + ')' + '\n')
                    f.write('\t};' + '\n')
                else:
                    f.write('\t\\addplot[style={fill=' + dataset.color + ', color=' + dataset.color +
                            '}, error bars/.cd, error bar style={black}, y dir=both, y explicit] coordinates {' + '\n')
                    for l, label in enumerate(self.labels):
                        f.write('\t\t(' + label + ',' + str(dataset.values[l]) + ') +- (' + str(
                            dataset.error_bars[l]) + ',' + str(dataset.error_bars[l]) + ')' + '\n')
                    f.write('\t};' + '\n')
                legend.append(dataset.label)

            f.write('\t\legend{' + ','.join(legend) + '}' + '\n')
            f.write('\t\end{axis}' + '\n')
            f.write('\\end{tikzpicture}' + '\n')
