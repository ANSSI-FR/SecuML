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

import json
import matplotlib.pyplot as plt
import pandas as pd

from SecuML.Tools import colors_tools
from SecuML.Tools import dir_tools

class ClusteringEvaluationMonitoring(object):

    def __init__(self, monitoring):
        self.monitoring = monitoring
        self.homogeneity_estimators = ['homogeneity', 'completeness', 'v_measure']
        self.adjusted_estimators = ['adjusted_rand_score', 'adjusted_mutual_info_score']
        self.evolution_file  = self.monitoring.AL_directory
        self.evolution_file += 'clustering_homogeneity_monitoring.csv'
        self.setOutputDirectory()

    def setOutputDirectory(self):
        self.output_directory  = self.monitoring.iteration_dir 
        self.output_directory += 'clustering_evaluation/'
        dir_tools.createDirectory(self.output_directory)

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
        if self.monitoring.iteration_number == 1:
            self.displayCsvHeader()
        annotations = self.monitoring.iteration.annotations
        clusterings = {'malicious': annotations.malicious, 'benign': annotations.benign}
        with open(self.evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iteration_number)
            for l in ['malicious', 'benign']:
                value = -1
                if l in clusterings:
                    clustering_analysis = clusterings[l].clustering_analysis
                    if clustering_analysis is not None:
                        for e in self.homogeneity_estimators + self.adjusted_estimators:
                            v.append(getattr(clustering_analysis.clustering.evaluation, e))
                    else:
                        v += [0, 0, 0]
                else:
                    for e in self.homogeneity_estimators + self.adjusted_estimators:
                        v.append(-1)
            print >>f, ','.join(map(str, v))

    def displayCsvHeader(self):
        with open(self.evolution_file, 'w') as f:
            header  = ['iteration']
            for l in ['malicious', 'benign']:
                for e in self.homogeneity_estimators + self.adjusted_estimators:
                    header.append(l + '_' + e)
            print >>f, ','.join(header)

    ##########################
    ## Evolution Monitoring ##
    ##########################

    def loadEvolutionMonitoring(self):
        with open(self.evolution_file, 'r') as f:
            self.data = pd.read_csv(f, header = 0, index_col = 0)

    def plotEvolutionMonitoring(self, estimator = None):
        if estimator is None:
            for e in self.homogeneity_estimators + self.adjusted_estimators:
                self.plotEvolutionMonitoring(estimator = e)
        else:
            iterations = range(self.monitoring.iteration_number)
            plt.clf()
            max_value = 1
            for l in ['malicious', 'benign']:
                color = colors_tools.getLabelColor(l)
                label = l + '_' + estimator
                plt.plot(iterations, self.data.loc[:][label],
                        label = l + ' clustering',
                        color = color, linewidth = 4, marker = 'o')
            plt.ylim(0, max_value)
            plt.xlabel('Iteration')
            plt.ylabel(estimator)
            plt.legend()
            filename  = self.output_directory
            filename += estimator + '_monitoring.png'
            plt.savefig(filename)
            plt.clf()
