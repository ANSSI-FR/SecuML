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
        self.monitoring = monitoring
        self.labels = ['benign', 'malicious']
        self.monitorings = {}
        for label in self.labels:
            self.monitorings[label] = FamiliesMonitoringOneLabel(monitoring, label)

    def generateMonitoring(self):
        for label in self.labels:
            self.monitorings[label].generateMonitoring()

    def exportMonitoring(self):
        monitoring_dir, evolution_dir = self.getOutputDirectories()
        for label in self.labels:
            self.monitorings[label].exportMonitoring(monitoring_dir, evolution_dir)

    def getOutputDirectories(self):
        monitoring_dir = self.monitoring.iteration_dir + 'families_monitoring/'
        dir_tools.createDirectory(monitoring_dir)

        evolution_dir  = self.monitoring.al_dir + 'families_monitoring/'
        if self.monitoring.iteration_number == 1:
            dir_tools.createDirectory(evolution_dir)

        return monitoring_dir, evolution_dir


class FamiliesMonitoringOneLabel(object):

    def __init__(self, monitoring, label):
        self.monitoring = monitoring
        self.label = label
        instances = self.monitoring.iteration.datasets.instances
        if instances.hasTrueLabels():
            self.families = list(instances.getFamiliesValues(label = self.label, true_labels = True))
        else:
            self.families = list(instances.getFamiliesValues(label = self.label))

    def generateMonitoring(self):
        return

    def getOutputFiles(self, monitoring_dir, evolution_dir):
        evolution_file = evolution_dir + self.label + '_families_monitoring.csv'
        return evolution_file

    def exportMonitoring(self, monitoring_dir, evolution_dir):
        evolution_file = self.getOutputFiles(monitoring_dir, evolution_dir)
        self.displayCsvLine(evolution_file)

        instances = self.monitoring.iteration.datasets.instances
        if instances.hasTrueLabels():
            self.plotEvolutionMonitoring(evolution_file, monitoring_dir)

    #############################
    #############################
    ##### Private functions #####
    #############################
    #############################

    def displayCsvLine(self, evolution_file, label = None):
        if self.monitoring.iteration_number == 1:
            self.displayCsvHeader(evolution_file)
        datasets = self.monitoring.iteration.datasets
        annotated_instances = datasets.getAnnotatedInstances(label= self.label)
        self.families_annotations = []
        for family in self.families:
            self.families_annotations.append(len(annotated_instances.getFamilyIds(family)))
        with open(evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iteration_number)
            v += self.families_annotations
            print >>f, ','.join(map(str, v))

    def displayCsvHeader(self, evolution_file):
        with open(evolution_file, 'w') as f:
            header  = ['iteration']
            header += self.families
            print >>f, ','.join(header)

    def loadEvolutionMonitoring(self, evolution_file):
        with open(evolution_file, 'r') as f:
            data = pd.read_csv(f, header = 0, index_col = 0)
            return data

    def plotEvolutionMonitoring(self, evolution_file, monitoring_dir):
        data = self.loadEvolutionMonitoring(evolution_file)

        barplot = BarPlot(self.families)
        for i in range(data.shape[0]):
            dataset = PlotDataset([data.iloc[i, 1]], str(i))
            barplot.addDataset(dataset)
        filename  = monitoring_dir
        filename += self.label + '_families_evolution.json'
        with open(filename, 'w') as f:
            barplot.exportJson(f)
