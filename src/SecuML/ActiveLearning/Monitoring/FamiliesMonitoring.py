## SecuML
## Copyright (C) 2016-2017  ANSSI
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

import pandas as pd

from SecuML.Plots.PlotDataset import PlotDataset
from SecuML.Plots.BarPlot import BarPlot
from SecuML.Tools import dir_tools

class FamiliesMonitoring(object):

    def __init__(self, monitoring):
        self.createOutputDirectories(monitoring)
        self.labels = ['benign', 'malicious']
        self.monitorings = {}
        for label in self.labels:
            self.monitorings[label] = FamiliesMonitoringOneLabel(monitoring, label, self.output_directory)

    def generateMonitoring(self):
        self.iterationMonitoring()
        self.evolutionMonitoring()

    def iterationMonitoring(self):
        for label in self.labels:
            self.monitorings[label].iterationMonitoring()

    def evolutionMonitoring(self):
        for label in self.labels:
            self.monitorings[label].evolutionMonitoring()

    def createOutputDirectories(self, monitoring):
        self.output_directory  = monitoring.iteration_dir
        self.output_directory += 'families_monitoring/'
        dir_tools.createDirectory(self.output_directory)
        if monitoring.iteration_number == 1:
            output_directory  = monitoring.AL_directory
            output_directory += 'families_monitoring/'
            dir_tools.createDirectory(output_directory)

class FamiliesMonitoringOneLabel(object):

    def __init__(self, monitoring, label, output_directory):
        self.monitoring = monitoring
        self.output_directory = output_directory
        self.label = label
        self.evolution_file  = self.monitoring.AL_directory + 'families_monitoring/'
        self.evolution_file += self.label + '_families_monitoring.csv'
        instances = self.monitoring.iteration.datasets.instances
        if instances.hasTrueLabels():
            self.families = list(instances.getFamiliesValues(label = self.label, true_labels = True))
        else:
            self.families = list(instances.getFamiliesValues(label = self.label))

    def iterationMonitoring(self):
        self.displayCsvLine()

    # When there is no ground truth labels, the number of families
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
        if self.monitoring.iteration_number == 1:
            self.displayCsvHeader()
        datasets = self.monitoring.iteration.datasets
        annotated_instances = datasets.getAnnotatedInstances(label= self.label)
        self.families_annotations = []
        for family in self.families:
            self.families_annotations.append(len(annotated_instances.getFamilyIds(family)))
        with open(self.evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iteration_number)
            v += self.families_annotations
            print >>f, ','.join(map(str, v))

    def displayCsvHeader(self):
        with open(self.evolution_file, 'w') as f:
            header  = ['iteration']
            header += self.families
            print >>f, ','.join(header)

    ##########################
    ## Evolution Monitoring ##
    ##########################

    def loadEvolutionMonitoring(self):
        with open(self.evolution_file, 'r') as f:
            self.data = pd.read_csv(f, header = 0, index_col = 0)

    def plotEvolutionMonitoring(self):
        barplot = BarPlot(self.families)
        for i in range(self.data.shape[0]):
            dataset = PlotDataset([self.data.iloc[i, 1]], str(i))
            barplot.addDataset(dataset)
        filename  = self.output_directory
        filename += self.label + '_families_evolution.json'
        with open(filename, 'w') as f:
            barplot.exportJson(f)
