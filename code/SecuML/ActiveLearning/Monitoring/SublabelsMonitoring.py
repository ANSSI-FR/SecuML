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

from SecuML.Plots.BarPlot import BarPlot
from SecuML.Tools import dir_tools

class SublabelsMonitoring(object):

    def __init__(self, monitoring):
        self.setOutputDirectory(monitoring)
        self.labels = ['benign', 'malicious']
        self.monitorings = {}
        for label in self.labels:
            self.monitorings[label] = SublabelsMonitoringOneLabel(monitoring, label, self.output_directory)
    
    def iterationMonitoring(self):
        for label in self.labels:
            self.monitorings[label].iterationMonitoring()

    def evolutionMonitoring(self):
        for label in self.labels:
            self.monitorings[label].evolutionMonitoring()
        
    def setOutputDirectory(self, monitoring):
        self.output_directory  = monitoring.iteration_dir 
        self.output_directory += 'sublabels_monitoring/'
        dir_tools.createDirectory(self.output_directory)

class SublabelsMonitoringOneLabel(object):

    def __init__(self, monitoring, label, output_directory):
        self.monitoring = monitoring
        self.output_directory = output_directory
        self.label = label
        self.evolution_file  = self.monitoring.AL_directory
        self.evolution_file += self.label + '_sublabels_monitoring.csv'
        instances = self.monitoring.iteration.datasets.instances
        if instances.hasTrueLabels():
            self.sublabels = list(instances.getSublabelsValues(label = self.label, true_labels = True))
        else:
            self.sublabels = list(instances.getSublabelsValues(label = self.label))
    
    def iterationMonitoring(self):
        self.displayCsvLine()
        self.plotIterationMonitoring()

    # When there is no ground truth labels, the number of sublabels
    # is unknown at the begining
    def evolutionMonitoring(self):
        instances = self.monitoring.iteration.datasets.instances
        if instances.hasTrueLabels():
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

    def displayCsvLine(self, label = None):
        exp = self.monitoring.iteration.experiment
        if self.monitoring.iteration_number == 1:
            self.displayCsvHeader()
        datasets = self.monitoring.iteration.datasets
        annotated_instances = datasets.getAnnotatedInstances(label= self.label)
        self.sublabels_annotations = []
        for sublabel in self.sublabels:
            self.sublabels_annotations.append(len(annotated_instances.getSublabelIds(sublabel)))
        with open(self.evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iteration_number)
            v += self.sublabels_annotations
            print >>f, ','.join(map(str, v))

    def displayCsvHeader(self):
        with open(self.evolution_file, 'w') as f:
            header  = ['iteration']
            header += self.sublabels
            print >>f, ','.join(header)
    
    def plotIterationMonitoring(self):
        barplot = BarPlot(self.sublabels)
        barplot.addDataset(self.sublabels_annotations, 'blue', 'Num Annotations')
        filename  = self.output_directory
        filename += self.label + '_sublabels_monitoring.json'
        with open(filename, 'w') as f:
            barplot.display(f)

    ##########################
    ## Evolution Monitoring ##
    ##########################

    def loadEvolutionMonitoring(self):
        with open(self.evolution_file, 'r') as f:
            self.data = pd.read_csv(f, header = 0, index_col = 0)

    def plotEvolutionMonitoring(self):
        barplot = BarPlot(self.sublabels)
        for i in range(self.data.shape[0]):
            barplot.addDataset(list(self.data.iloc[i, 1:]), 'blue', str(i))
        filename  = self.output_directory
        filename += self.label + '_sublabels_evolution.json'
        with open(filename, 'w') as f:
            barplot.display(f)
