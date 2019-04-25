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

import matplotlib.pyplot as plt


class LinePlot(object):

    def __init__(self, title=None, xlabel=None, ylabel=None, xmin=None,
                 xmax=None, ymin=None, ymax=None):
        self.datasets = []
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def add_dataset(self, dataset):
        self.datasets.append(dataset)

    def to_png(self, filename):
        plt.clf()
        for dataset in self.datasets:
            if dataset.error_bars is not None:
                plt.errorbar(dataset.xvalues, dataset.values,
                             yerr=dataset.error_bars, label=dataset.label)
            else:
                plt.plot(dataset.xvalues, dataset.values, label=dataset.label)
        if self.xlabel is not None:
            plt.xlabel(self.xlabel)
        if self.ylabel is not None:
            plt.ylabel(self.ylabel)
        if self.title is not None:
            plt.title(self.title)
        plt.legend(loc='lower right')
        plt.savefig(filename)
        plt.clf()

    def to_pgf_plot(self, filename, standalone=False):
        with open(filename, 'w') as f:
            if standalone:
                f.write('\\documentclass[crop]{standalone}\n')
                f.write('\\usepackage{pgfplots}\n')
                f.write('\\usepackage{tikz}\n')
                f.write('\\begin{document}\n')
            f.write('\\begin{tikzpicture}\n'
                    '\t\\begin{axis} [\n')
            if self.xlabel is not None:
                f.write('\t\txlabel=\\large %s,\n' % self.xlabel)
            if self.ylabel is not None:
                f.write('\t\tylabel=\\large %s,\n' % self.ylabel)
            if self.title is not None:
                f.write('\t\ttitle = %s,\n' % self.title)
            for limit in ['xmin', 'xmax', 'ymin', 'ymax']:
                if getattr(self, limit) is not None:
                    f.write('\t\t%s = %f,\n' % (limit, getattr(self, limit)))
            f.write('\t\txlabel near ticks,\n'
                    '\t\tylabel near ticks,\n'
                    '\t\tlegend pos = south east,\n'
                    '\t\tlegend cell align = left\n'
                    '\t]\n')
            for dataset in self.datasets:
                f.write('\t\\addplot[color=%s, mark=none, ultra thick, '
                        'dashdotted] coordinates {\n' % dataset.label)
                for x, y in zip(dataset.xvalues, dataset.values):
                    f.write('\t\t(%f,%f)\n' % (x, y))
                f.write('\t};\n')
                f.write('\t\\definecolor{%s}{HTML}{%s}\n'
                        % (dataset.label, dataset.color[1:].upper()))
                f.write('\t\\addlegendentry{%s}\n' % dataset.label)
                if dataset.error_bars is not None:
                    f.write('\t\\addplot[color=%s, only marks, '
                            'error bars/y dir=both, error bars/y explicit, '
                            'mark options={%s}, forget plot]'
                            'coordinates {\n'
                            % (dataset.label, dataset.label))
                    for x, y, err in zip(dataset.xvalues, dataset.values,
                                         dataset.error_bars):
                        f.write('\t\t(%f,%f) +- (0,%f)\n' % (x, y, err))
                    f.write('\t};\n')
            f.write('\t\\end{axis}\n'
                    '\\end{tikzpicture}\n')
            if standalone:
                f.write('\\end{document}\n')
