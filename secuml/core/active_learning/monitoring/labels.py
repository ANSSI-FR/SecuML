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

import csv
import json
import matplotlib.pyplot as plt
import os
import os.path as path
import pandas as pd

from secuml.core.data.labels_tools import BENIGN, MALICIOUS
from secuml.core.tools.color import get_label_color


class LabelsMonitoring(object):

    def __init__(self, monitoring):
        self.monitoring = monitoring
        instances = self.monitoring.datasets.instances
        self.has_ground_truth = instances.has_ground_truth()

    def generate(self):
        instances = self.monitoring.datasets.instances
        self.stats = {}
        for l in [MALICIOUS, BENIGN]:
            self.stats[l] = {}
            self.stats[l]['annotations'] = instances.num_instances(label=l)
            self.stats[l]['families'] = len(
                instances.annotations.get_families_values(label=l))
        self.stats['global'] = {}
        for k in ['annotations', 'families']:
            self.stats['global'][k] = (self.stats[MALICIOUS][k] +
                                       self.stats[BENIGN][k])
        self.stats['unlabeled'] = (instances.num_instances() -
                                   self.stats['global']['annotations'])

    def export(self, al_dir, iteration_dir):
        monitoring_dir, evolution_dir = self.get_ouput_dirs(al_dir,
                                                            iteration_dir)
        evolution_file = path.join(evolution_dir, 'labels_monitoring.csv')
        monitoring_file = path.join(monitoring_dir, 'labels_monitoring.json')
        self.export_to_json(monitoring_file)
        self.display_csv_line(evolution_file)
        self.plot_evolution(evolution_file, monitoring_dir)

    def get_ouput_dirs(self, al_dir, iteration_dir):
        monitoring_dir = path.join(iteration_dir, 'labels_monitoring')
        os.makedirs(monitoring_dir)
        evolution_dir = path.join(al_dir, 'labels_monitoring')
        if self.monitoring.iter_num == 1:
            os.makedirs(evolution_dir)
        return monitoring_dir, evolution_dir

    def export_to_json(self, monitoring_file):
        with open(monitoring_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def display_csv_line(self, evolution_file):
        if self.monitoring.iter_num == 1:
            self.display_csv_header(evolution_file)
        with open(evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iter_num)
            for k in ['annotations', 'families']:
                for l in [MALICIOUS, BENIGN, 'global']:
                    v.append(self.stats[l][k])
            csv_writer = csv.writer(f)
            csv_writer.writerow(v)

    def display_csv_header(self, evolution_file):
        with open(evolution_file, 'w') as f:
            header = ['iteration']
            for k in ['annotations_', 'families_']:
                for l in [MALICIOUS, BENIGN, 'global']:
                    header.append(k + l)
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)

    def load_evolution(self, evolution_file):
        with open(evolution_file, 'r') as f:
            data = pd.read_csv(f, header=0, index_col=0)
        self.evolutions = {}
        for l in ['global', MALICIOUS, BENIGN]:
            self.evolutions[l] = {}
            for k in ['annotations', 'families']:
                self.evolutions[l][k] = list(data.loc[:][k + '_' + l])

    def plot_evolution(self, evolution_file, iteration_dir):
        self.load_evolution(evolution_file)
        self.plot_families_evolution(iteration_dir)

    def plot_families_evolution(self, iteration_dir):
        annotations = self.evolutions['global']['annotations']
        plt.clf()
        if self.has_ground_truth:
            max_value = 1
        else:
            max_value = max(self.stats[MALICIOUS]['families'],
                            self.stats[BENIGN]['families'])
        for l in [MALICIOUS, BENIGN]:
            evolution = self.evolutions[l]['families']
            num_families = 0
            if self.has_ground_truth:
                instances = self.monitoring.datasets.instances
                num_families = len(
                    instances.ground_truth.get_families_values(label=l))
                if num_families > 0:
                    evolution = [x / num_families for x in evolution]
            plt.plot(annotations, evolution, label=l.title(),
                     color=get_label_color(l), linewidth=4, marker='o')
        plt.ylim(0, max_value)
        plt.xlabel('Num Annotations')
        if self.has_ground_truth and num_families > 0:
            plt.ylabel('Prop. Families Discovered')
        else:
            plt.ylabel('Num. Families Discovered')
        lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                         ncol=2, mode='expand', borderaxespad=0.,
                         fontsize='x-large')
        filename = path.join(iteration_dir, 'families_monitoring.png')
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()
