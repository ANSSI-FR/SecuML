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

import csv
import matplotlib.pyplot as plt
import pandas as pd


class ExecutionTimeMonitoring(object):

    def __init__(self, monitoring):
        self.monitoring = monitoring

    def generateMonitoring(self):
        return

    def exportMonitoring(self, al_dir, iteration_dir):
        monitoring_dir, evolution_file = self.getOutputDirectories(
            al_dir, iteration_dir)
        self.displayCsvLine(evolution_file)
        self.plotEvolutionMonitoring(evolution_file, monitoring_dir)

    def getOutputDirectories(self, al_dir, iteration_dir):
        monitoring_dir = iteration_dir
        evolution_file = al_dir + 'execution_time_monitoring.csv'
        return monitoring_dir, evolution_file

    def displayCsvLine(self, evolution_file):
        if self.monitoring.iteration_number == 1:
            self.displayCsvHeader(evolution_file)
        iteration = self.monitoring.iteration
        with open(evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iteration_number)
            v += iteration.annotations.executionTimeMonitoring()
            csv_writer = csv.writer(f)
            csv_writer.writerow(v)

    def displayCsvHeader(self, evolution_file):
        iteration = self.monitoring.iteration
        with open(evolution_file, 'w') as f:
            header = ['iteration']
            header += iteration.annotations.executionTimeHeader()
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)

    def loadEvolutionMonitoring(self, evolution_file):
        with open(evolution_file, 'r') as f:
            data = pd.read_csv(f, header=0, index_col=0)
            return data

    def plotEvolutionMonitoring(self, evolution_file, monitoring_dir):
        data = self.loadEvolutionMonitoring(evolution_file)
        iterations = list(range(1, self.monitoring.iteration_number + 1))
        plt.clf()
        max_value = data.max().max()
        annotations = self.monitoring.iteration.annotations
        monitoring = annotations.executionTimeDisplay()
        header = annotations.executionTimeHeader()
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
        filename = monitoring_dir
        filename += 'execution_time_monitoring.png'
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        filename = monitoring_dir
        filename += 'execution_time_monitoring.eps'
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight',
                    dpi=1000, format='eps')
        plt.clf()
