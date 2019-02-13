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

from secuml.core.tools.plots.dataset import PlotDataset


class SuggestionsAccuracyCounts(object):

    def __init__(self, monitoring, kind, labels_families):
        self.monitoring = monitoring
        self.kind = kind
        self.labels_families = labels_families
        self.init_counts()

    def init_counts(self):
        self.num_annotations = 0
        self.num_suggestions = 0
        self.true_suggestions = 0
        self.false_suggestions = 0
        self.no_suggestion = 0

    def add_annotation(self, suggestion, answer):
        self.num_annotations += 1
        if suggestion is None:
            self.no_suggestion += 1
        elif suggestion == answer:
            self.true_suggestions += 1
            self.num_suggestions += 1
        else:
            self.false_suggestions += 1
            self.num_suggestions += 1

    def export(self, monitoring_dir, evolution_dir):
        filename = '_'.join([self.labels_families, self.kind,
                             'suggestions.csv'])
        evolution_file = path.join(evolution_dir, filename)
        self.display_csv_line(evolution_file)
        self.plot_evolution(evolution_file, monitoring_dir)

    def display_csv_line(self, evolution_file):
        if self.monitoring.iter_num == 1:
            self.display_csv_header(evolution_file)
        with open(evolution_file, 'a') as f:
            v = [self.monitoring.iter_num]
            v.extend([self.true_suggestions, self.false_suggestions,
                      self.no_suggestion, self.num_suggestions,
                      self.num_annotations])
            csv_writer = csv.writer(f)
            csv_writer.writerow(v)

    def display_csv_header(self, evolution_file):
        with open(evolution_file, 'w') as f:
            header = ['iteration']
            header.extend(['true_suggestions', 'false_suggestions',
                           'no_suggestion', 'num_suggestions',
                           'num_annotations'])
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)

    def load_evolution(self, evolution_file):
        with open(evolution_file, 'r') as f:
            data = pd.read_csv(f, header=0, index_col=0)
            return data

    def plot_evolution(self, evolution_file, monitoring_dir):
        data = self.load_evolution(evolution_file)
        if self.labels_families == 'labels':
            title = 'Labels Suggestions Accuracy'
        elif self.labels_families == 'families':
            title = 'Families Suggestions Accuracy'
        plot = PlotDataset(data['true_suggestions'] /
                           data['num_suggestions'], title)
        iterations = list(range(self.monitoring.iter_num))
        plt.clf()
        max_value = 1
        plt.plot(iterations, plot.values,
                 label=plot.label,
                 color=plot.color,
                 linewidth=plot.linewidth,
                 marker=plot.marker)
        plt.ylim(0, max_value)
        plt.xlabel('Iteration')
        plt.ylabel('Suggestions Accuracy')
        lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                         ncol=2, mode='expand', borderaxespad=0.,
                         fontsize='large')
        filename = '_'.join([self.labels_families,
                             self.kind,
                             'suggestions.png'])
        filename = path.join(monitoring_dir, filename)
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()
        self.data = data


class SuggestionsAccuracyLabelsFamilies(object):

    def __init__(self, monitoring, labels_families):
        self.labels_families = labels_families
        self.init_counts(monitoring)

    def init_counts(self, monitoring):
        self.all_counts = SuggestionsAccuracyCounts(
                monitoring,
                'all',
                self.labels_families)
        self.high_confidence_counts = SuggestionsAccuracyCounts(
                monitoring,
                'high_confidence',
                self.labels_families)

    def add_annotation(self, suggestion, answer, confidence):
        self.all_counts.add_annotation(suggestion, answer)
        if confidence == 'low':
            self.high_confidence_counts.add_annotation(None, answer)
        elif confidence == 'high':
            self.high_confidence_counts.add_annotation(suggestion, answer)

    def generate(self):
        return

    def export(self, monitoring_dir, evolution_dir, kind=None):
        if kind is None:
            self.export(monitoring_dir, evolution_dir, kind='all')
            self.export(monitoring_dir, evolution_dir, kind='high_confidence')
            return
        if kind == 'all':
            counts = self.all_counts
        elif kind == 'high_confidence':
            counts = self.high_confidence_counts
        counts.export(monitoring_dir, evolution_dir)


class SuggestionsAccuracy(object):

    def __init__(self, monitoring):
        self.monitoring = monitoring
        self.labels_accuracy = SuggestionsAccuracyLabelsFamilies(monitoring,
                                                                 'labels')
        self.families_accuracy = SuggestionsAccuracyLabelsFamilies(monitoring,
                                                                   'families')

    def add_annotation(self, suggested_label, suggested_family, label, family,
                       confidence):
        self.labels_accuracy.add_annotation(suggested_label, label, confidence)
        self.families_accuracy.add_annotation(suggested_family, family,
                                              confidence)

    def generate(self):
        self.labels_accuracy.generate()
        self.families_accuracy.generate()

    def export(self, al_dir, iteration_dir):
        monitoring_dir, evolution_dir = self.get_ouput_dirs(al_dir,
                                                            iteration_dir)
        self.labels_accuracy.export(monitoring_dir, evolution_dir)
        self.families_accuracy.export(monitoring_dir, evolution_dir)
        self.plot_evolution(monitoring_dir)

    def plot_evolution(self, monitoring_dir):
        iterations = list(range(1, self.monitoring.iter_num + 1))
        plt.clf()
        # Labels
        data = self.labels_accuracy.high_confidence_counts.data
        values = data['true_suggestions'] / data['num_suggestions']
        plot = PlotDataset(values, 'Labels Suggestions')
        max_value = 1
        plt.plot(iterations, plot.values,
                 label=plot.label,
                 color=plot.color,
                 linewidth=plot.linewidth,
                 marker=plot.marker)
        # Families
        data = self.families_accuracy.high_confidence_counts.data
        values = data['true_suggestions'] / data['num_suggestions']
        plot = PlotDataset(values, 'Families Suggestions')
        max_value = 1
        plt.plot(iterations, plot.values,
                 label=plot.label,
                 color='purple',
                 linewidth=plot.linewidth,
                 marker=plot.marker)
        # Plot
        plt.ylim(0, max_value)
        plt.xlabel('Iteration')
        plt.ylabel('Suggestions Accuracy')
        lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                         ncol=2, mode='expand', borderaxespad=0.,
                         fontsize='large')
        filename = path.join(monitoring_dir,
                             'labels_families_high_confidence_suggestions.png')
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()

    def get_ouput_dirs(self, al_dir, iteration_dir):
        monitoring_dir = path.join(iteration_dir, 'suggestions_accuracy')
        os.makedirs(monitoring_dir)

        evolution_dir = path.join(al_dir, 'suggestions_accuracy')
        if self.monitoring.iter_num == 1:
            os.makedirs(evolution_dir)

        return monitoring_dir, evolution_dir
