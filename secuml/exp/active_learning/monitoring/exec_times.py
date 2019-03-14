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

import csv
import matplotlib.pyplot as plt
import os.path as path
import pandas as pd


class ExecutionTimesMonitoring(object):

    def __init__(self, iteration):
        self.iteration = iteration

    def generate(self):
        return

    def export(self, al_dir, iter_dir):
        monitoring_dir, evolution_file = self._get_output_dirs(al_dir,
                                                               iter_dir)
        self._display_csv_line(evolution_file)
        self._plot_evolution(evolution_file, monitoring_dir)

    def _display_csv_line(self, evolution_file):
        if self.iteration.iter_num == 1:
            self._display_csv_header(evolution_file)
        with open(evolution_file, 'a') as f:
            v = [self.iteration.iter_num]
            v.extend(self.iteration.strategy.get_exec_times())
            csv_writer = csv.writer(f)
            csv_writer.writerow(v)

    def _display_csv_header(self, evolution_file):
        with open(evolution_file, 'w') as f:
            header = ['iteration']
            header.extend(self.iteration.strategy.get_exec_times_header())
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)

    def _load_evolution(self, evolution_file):
        with open(evolution_file, 'r') as f:
            data = pd.read_csv(f, header=0, index_col=0)
            return data

    def _plot_evolution(self, evolution_file, monitoring_dir):
        data = self._load_evolution(evolution_file)
        iterations = list(range(1, self.iteration.iter_num + 1))
        plt.clf()
        max_value = data.max().max()
        monitoring = self.iteration.strategy.get_exec_times_display()
        header = self.iteration.strategy.get_exec_times_header()
        for i, m in enumerate(monitoring):
            label = header[i]
            plt.plot(iterations, data[label],
                     label=m.label,
                     linestyle=m.linestyle,
                     color=m.color, linewidth=m.linewidth, marker=m.marker)
        plt.ylim(0, max_value)
        plt.xlabel('Iteration')
        plt.ylabel('Execution Time (seconds)')
        lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                         ncol=2, mode='expand', borderaxespad=0.,
                         fontsize='large')
        filename = path.join(monitoring_dir, 'execution_times.png')
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        filename = path.join(monitoring_dir, 'execution_times.eps')
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight',
                    dpi=1000, format='eps')
        plt.clf()

    def _get_output_dirs(self, al_dir, iteration_dir):
        monitoring_dir = iteration_dir
        evolution_file = path.join(al_dir, 'execution_times.csv')
        return monitoring_dir, evolution_file
