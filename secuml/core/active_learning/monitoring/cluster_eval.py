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
import os
import os.path as path
import pandas as pd

from secuml.core.tools.color import get_label_color


class ClusteringEvaluationMonitoring(object):

    def __init__(self, monitoring):
        self.monitoring = monitoring
        self.homogeneity_estimators = [
            'homogeneity', 'completeness', 'v_measure']
        self.adjusted_estimators = [
            'adjusted_rand_score', 'adjusted_mutual_info_score']
        self.evolution_file = path.join(self.monitoring.AL_directory,
                                        'clustering_homogeneity_monitoring.csv')
        self.annotations = self.monitoring.iteration.annotations
        self.set_output_dir()

    def set_output_dir(self):
        self.output_dir = path.join(self.monitoring.iteration_dir,
                                    'clustering_evaluation')
        os.makedirs(self.output_dir)

    def iteration_monitoring(self):
        self.display_csv_line()

    def evolution_monitoring(self):
        self.load_evolution()
        self.plot_evolution()

    def display_csv_line(self):
        if self.monitoring.iter_num == 1:
            self.display_csv_header()
        clusterings = self.annotations.getClusteringsEvaluations()
        with open(self.evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iter_num)
            for l, evaluation in clusterings.items():
                if evaluation is not None:
                    for e in self.homogeneity_estimators + self.adjusted_estimators:
                        v.append(getattr(evaluation, e))
                else:
                    v += [0] * (len(self.homogeneity_estimators) +
                                len(self.adjusted_estimators))
            csv_writer = csv.writer(f)
            csv_writer.writerow(v)

    def display_csv_header(self):
        with open(self.evolution_file, 'w') as f:
            header = ['iteration']
            clusterings = self.annotations.getClusteringsEvaluations()
            for l in list(clusterings.keys()):
                for e in self.homogeneity_estimators + self.adjusted_estimators:
                    header.append(l + '_' + e)
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)

    def load_evolution(self):
        with open(self.evolution_file, 'r') as f:
            self.data = pd.read_csv(f, header=0, index_col=0)

    def plot_evolution(self, estimator=None):
        if estimator is None:
            for e in self.homogeneity_estimators + self.adjusted_estimators:
                self.plot_evolution(estimator=e)
        else:
            iterations = list(range(self.monitoring.iter_num))
            plt.clf()
            max_value = 1
            clusterings = self.annotations.getClusteringsEvaluations()
            for l in list(clusterings.keys()):
                label = l + '_' + estimator
                plt.plot(iterations, self.data.loc[:][label],
                         label='%s Clustering' % l.title(),
                         color=get_label_color(l), linewidth=4, marker='o')
            plt.ylim(0, max_value)
            plt.xlabel('Iteration')
            plt.ylabel(estimator)
            lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                             ncol=2, mode='expand', borderaxespad=0.,
                             fontsize='large')
            filename = path.join(self.output_dir,
                                 '%s_monitoring.png' % estimator)
            plt.savefig(filename, bbox_extra_artists=(lgd,),
                        bbox_inches='tight')
            plt.clf()
