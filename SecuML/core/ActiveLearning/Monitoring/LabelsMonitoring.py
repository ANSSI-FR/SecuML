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
import json
import matplotlib.pyplot as plt
import pandas as pd

from SecuML.core.Data import labels_tools
from SecuML.core.Tools import colors_tools
from SecuML.core.Tools import dir_tools


class LabelsMonitoring(object):

    def __init__(self, monitoring):
        self.monitoring = monitoring
        self.has_ground_truth = self.monitoring.datasets.instances.hasGroundTruth()

    def generateMonitoring(self):
        instances = self.monitoring.datasets.instances
        self.stats = {}
        for l in [labels_tools.MALICIOUS, labels_tools.BENIGN]:
            self.stats[l] = {}
            self.stats[l]['annotations'] = instances.numInstances(label=l)
            self.stats[l]['families'] = len(
                instances.annotations.getFamiliesValues(label=l))
        self.stats['global'] = {}
        for k in ['annotations', 'families']:
            self.stats['global'][k] = self.stats[labels_tools.MALICIOUS][k] + \
                self.stats[labels_tools.BENIGN][k]
        self.stats['unlabeled'] = instances.numInstances(
        ) - self.stats['global']['annotations']

    def exportMonitoring(self, al_dir, iteration_dir):
        monitoring_dir, evolution_dir = self.getOutputDirectories(
            al_dir, iteration_dir)
        evolution_file = evolution_dir + 'labels_monitoring.csv'
        self.jsonExport(monitoring_dir + 'labels_monitoring.json')
        self.displayCsvLine(evolution_file)
        self.plotEvolutionMonitoring(evolution_file, monitoring_dir)

    def getOutputDirectories(self, al_dir, iteration_dir):
        monitoring_dir = iteration_dir + 'labels_monitoring/'
        dir_tools.createDirectory(monitoring_dir)
        evolution_dir = al_dir + 'labels_monitoring/'
        if self.monitoring.iteration_number == 1:
            dir_tools.createDirectory(evolution_dir)
        return monitoring_dir, evolution_dir

    def jsonExport(self, monitoring_file):
        with open(monitoring_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def generateLabelMonitoring(self, label):
        datasets = self.monitoring.datasets
        monitoring = self.labeled_monitoring
        label_stats = monitoring.stats[label]
        label_stats.annotations = datasets.num_annotations[label]

    def displayCsvLine(self, evolution_file):
        if self.monitoring.iteration_number == 1:
            self.displayCsvHeader(evolution_file)
        with open(evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iteration_number)
            for k in ['annotations', 'families']:
                for l in [labels_tools.MALICIOUS, labels_tools.BENIGN, 'global']:
                    v.append(self.stats[l][k])
            csv_writer = csv.writer(f)
            csv_writer.writerow(v)

    def displayCsvHeader(self, evolution_file):
        with open(evolution_file, 'w') as f:
            header = ['iteration']
            for k in ['annotations_', 'families_']:
                for l in [labels_tools.MALICIOUS, labels_tools.BENIGN, 'global']:
                    header.append(k + l)
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)

    def loadEvolutionMonitoring(self, evolution_file):
        with open(evolution_file, 'r') as f:
            data = pd.read_csv(f, header=0, index_col=0)
        self.evolutions = {}
        for l in ['global', labels_tools.MALICIOUS, labels_tools.BENIGN]:
            self.evolutions[l] = {}
            for k in ['annotations', 'families']:
                self.evolutions[l][k] = list(data.loc[:][k + '_' + l])

    def plotEvolutionMonitoring(self, evolution_file, iteration_dir):
        self.loadEvolutionMonitoring(evolution_file)
        self.plotFamiliesEvolutionMonitoring(iteration_dir)

    def plotFamiliesEvolutionMonitoring(self, iteration_dir):
        annotations = self.evolutions['global']['annotations']
        plt.clf()
        if self.has_ground_truth:
            max_value = 1
        else:
            max_value = max(self.stats[labels_tools.MALICIOUS]['families'],
                            self.stats[labels_tools.BENIGN]['families'])
        for l in [labels_tools.MALICIOUS, labels_tools.BENIGN]:
            evolution = self.evolutions[l]['families']
            if self.has_ground_truth:
                instances = self.monitoring.datasets.instances
                num_families = len(
                    instances.ground_truth.getFamiliesValues(label=l))
                evolution = [x / num_families for x in evolution]
            color = colors_tools.getLabelColor(l)
            plt.plot(annotations, evolution,
                     label=l.title(),
                     color=color, linewidth=4, marker='o')
        plt.ylim(0, max_value)
        plt.xlabel('Num Annotations')
        if self.has_ground_truth:
            plt.ylabel('Prop. Families Discovered')
        else:
            plt.ylabel('Num. Families Discovered')
        lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                         ncol=2, mode='expand', borderaxespad=0.,
                         fontsize='x-large')
        filename = iteration_dir
        filename += 'families_monitoring.png'
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()
