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
import pandas as pd

from SecuML.Tools import colors_tools

class ExecutionTimeMonitoring(object):

    def __init__(self, monitoring):
        self.monitoring = monitoring
        self.evolution_file  = self.monitoring.AL_directory
        self.evolution_file += 'execution_time_monitoring.csv'

    def iterationMonitoring(self):
        self.displayCsvLine()

    def evolutionMonitoring(self):
        self.loadEvolutionMonitoring()
        self.plotEvolutionMonitoring()

    #############################
    #############################
    ##### Private functions #####
    #############################
    #############################

    ##########################
    ## Iteration Monitoring ##
    ##########################

    def displayCsvLine(self):
        exp = self.monitoring.iteration.experiment
        self.ilab = exp.labeling_method == 'ILAB'
        if self.monitoring.iteration_number == 1:
            self.displayCsvHeader()
        iteration = self.monitoring.iteration
        with open(self.evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iteration_number)
            v.append(iteration.train_test_validation.training_predicting_time)
            if self.ilab:
                v.append(iteration.annotations.malicious.clustering_time)
                v.append(iteration.annotations.benign.clustering_time)
            print >>f, ','.join(map(str, v))

    def displayCsvHeader(self):
        with open(self.evolution_file, 'w') as f:
            header  = ['iteration']
            header.append('learning_predicting')
            if self.ilab:
                for l in ['malicious', 'benign']:
                    header.append(l + '_clustering')
            print >>f, ','.join(header)

    ##########################
    ## Evolution Monitoring ##
    ##########################

    def loadEvolutionMonitoring(self):
        with open(self.evolution_file, 'r') as f:
            self.data = pd.read_csv(f, header = 0, index_col = 0)

    def plotEvolutionMonitoring(self):
        iterations = range(self.monitoring.iteration_number)
        plt.clf()
        max_value = self.data.max().max()
        plt.plot(iterations, self.data.loc[:]['learning_predicting'],
                label = 'Learning + Predicting',
                color = 'blue', linewidth = 4, marker = 'o')
        if self.ilab:
            for l in ['malicious', 'benign']:
                color = colors_tools.getLabelColor(l)
                label = l + '_clustering'
                plt.plot(iterations, self.data.loc[:][label],
                        label = l.title() + ' Clustering', 
                        linestyle = 'dashed',
                        color = color, linewidth = 4, marker = 'o')
        plt.ylim(0, max_value)
        plt.xlabel('Iteration')
        plt.ylabel('Execution Time (seconds)')
        lgd = plt.legend(bbox_to_anchor = (0., 1.02, 1., .102), loc = 3,
                ncol = 2, mode = 'expand', borderaxespad = 0.,
                fontsize = 'x-large')
        filename  = self.monitoring.iteration_dir
        filename += 'execution_time_monitoring.png'
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        filename  = self.monitoring.iteration_dir
        filename += 'execution_time_monitoring.eps'
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight',
                dpi=1000, format='eps')
        plt.clf()
