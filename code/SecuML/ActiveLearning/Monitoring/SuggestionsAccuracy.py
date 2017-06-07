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

from __future__ import division
import matplotlib.pyplot as plt
import pandas as pd

from SecuML.Plots.PlotDataset import PlotDataset
from SecuML.Tools import dir_tools

class SuggestionsAccuracyCounts(object):

    def __init__(self, monitoring, kind, labels_families):
        self.monitoring  = monitoring
        self.kind = kind
        self.labels_families = labels_families
        self.setOutputDirectory()
        self.setEvolutionFileName()
        self.initCounts()

    def initCounts(self):
        self.num_annotations   = 0
        self.num_suggestions   = 0
        self.true_suggestions  = 0
        self.false_suggestions = 0
        self.no_suggestion     = 0

    def setOutputDirectory(self):
        self.output_directory  = self.monitoring.iteration_dir
        self.output_directory += 'suggestions_accuracy/'

    def setEvolutionFileName(self):
        self.evolution_file  = self.monitoring.AL_directory
        self.evolution_file += 'suggestions_accuracy/'
        self.evolution_file += self.labels_families
        self.evolution_file +=  '_' + self.kind + '_suggestions.csv'

    def addAnnotation(self, suggestion, answer):
        self.num_annotations += 1
        if suggestion is None:
            self.no_suggestion += 1
        elif suggestion == answer:
            self.true_suggestions += 1
            self.num_suggestions  += 1
        else:
            self.false_suggestions += 1
            self.num_suggestions   += 1

    def displayCsvLine(self):
        if self.monitoring.iteration_number == 1:
            self.displayCsvHeader()
        with open(self.evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iteration_number)
            v.append(self.true_suggestions)
            v.append(self.false_suggestions)
            v.append(self.no_suggestion)
            v.append(self.num_suggestions)
            v.append(self.num_annotations)
            print >>f, ','.join(map(str, v))

    def displayCsvHeader(self):
        with open(self.evolution_file, 'w') as f:
            header  = ['iteration']
            header += ['true_suggestions', 'false_suggestions', 'no_suggestion',
                       'num_suggestions', 'num_annotations']
            print >>f, ','.join(header)

    def evolutionMonitoring(self):
        self.loadEvolutionMonitoring()
        self.plotEvolutionMonitoring()

    def loadEvolutionMonitoring(self):
        with open(self.evolution_file, 'r') as f:
            self.data = pd.read_csv(f, header = 0, index_col = 0)

    def plotEvolutionMonitoring(self):
        if self.labels_families == 'labels':
            title = 'Labels Suggestions Accuracy'
        elif self.labels_families == 'families':
            title = 'Families Suggestions Accuracy'
        plot = PlotDataset(self.data['true_suggestions'] / self.data['num_suggestions'], title)
        iterations = range(self.monitoring.iteration_number)
        plt.clf()
        max_value = 1
        plt.plot(iterations, plot.values,
                label = plot.label,
                color = plot.color,
                linewidth = plot.linewidth,
                marker = plot.marker)
        plt.ylim(0, max_value)
        plt.xlabel('Iteration')
        plt.ylabel('Suggestions Accuracy')
        lgd = plt.legend(bbox_to_anchor = (0., 1.02, 1., .102), loc = 3,
                ncol = 2, mode = 'expand', borderaxespad = 0.,
                fontsize = 'large')
        filename  = self.output_directory
        filename += self.labels_families + '_' + self.kind + '_suggestions.png'
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()

class SuggestionsAccuracyLabelsFamilies(object):

    def __init__(self, monitoring, labels_families):
        self.labels_families = labels_families
        self.initCounts(monitoring)

    def initCounts(self, monitoring):
        self.all_counts = SuggestionsAccuracyCounts(monitoring,
                'all', self.labels_families)
        self.high_confidence_counts = SuggestionsAccuracyCounts(monitoring,
                'high_confidence', self.labels_families)

    def addAnnotation(self, suggestion, answer, confidence):
        self.all_counts.addAnnotation(suggestion, answer)
        if confidence == 'low':
            self.high_confidence_counts.addAnnotation(None, answer)
        elif confidence == 'high':
            self.high_confidence_counts.addAnnotation(suggestion, answer)

    def iterationMonitoring(self, kind = None):
        if kind is None:
            self.iterationMonitoring(kind = 'all')
            self.iterationMonitoring(kind = 'high_confidence')
            return
        if kind == 'all':
            counts = self.all_counts
        elif kind == 'high_confidence':
            counts = self.high_confidence_counts
        counts.displayCsvLine()

    def evolutionMonitoring(self, kind = None):
        if kind is None:
            self.evolutionMonitoring(kind = 'all')
            self.evolutionMonitoring(kind = 'high_confidence')
            return
        if kind == 'all':
            counts = self.all_counts
        elif kind == 'high_confidence':
            counts = self.high_confidence_counts
        counts.evolutionMonitoring()

class SuggestionsAccuracy(object):

    def __init__(self, monitoring):
        self.monitoring        = monitoring
        self.labels_accuracy   = SuggestionsAccuracyLabelsFamilies(monitoring, 'labels')
        self.families_accuracy = SuggestionsAccuracyLabelsFamilies(monitoring, 'families')
        self.createOutputDirectories()

    def addAnnotation(self, suggested_label, suggested_family, label, family, confidence):
        self.labels_accuracy.addAnnotation(suggested_label, label, confidence)
        self.families_accuracy.addAnnotation(suggested_family, family, confidence)

    def generateMonitoring(self):
        self.iterationMonitoring()
        self.evolutionMonitoring()

    def iterationMonitoring(self):
        self.labels_accuracy.iterationMonitoring()
        self.families_accuracy.iterationMonitoring()

    def evolutionMonitoring(self):
        self.labels_accuracy.evolutionMonitoring()
        self.families_accuracy.evolutionMonitoring()
        self.plotEvolutionMonitoring()

    def plotEvolutionMonitoring(self):
        iterations = range(self.monitoring.iteration_number)
        plt.clf()
        # Labels
        data = self.labels_accuracy.high_confidence_counts.data
        values = data['true_suggestions'] / data['num_suggestions']
        plot = PlotDataset(values, 'Labels Suggestions')
        max_value = 1
        plt.plot(iterations, plot.values,
                label = plot.label,
                color = plot.color,
                linewidth = plot.linewidth,
                marker = plot.marker)
        # Families
        data = self.families_accuracy.high_confidence_counts.data
        values = data['true_suggestions'] / data['num_suggestions']
        plot = PlotDataset(values, 'Families Suggestions')
        max_value = 1
        plt.plot(iterations, plot.values,
                 label = plot.label,
                 color = 'purple',
                 linewidth = plot.linewidth,
                 marker = plot.marker)
        # Plot
        plt.ylim(0, max_value)
        plt.xlabel('Iteration')
        plt.ylabel('Suggestions Accuracy')
        lgd = plt.legend(bbox_to_anchor = (0., 1.02, 1., .102), loc = 3,
                ncol = 2, mode = 'expand', borderaxespad = 0.,
                fontsize = 'large')
        filename  = self.output_directory
        filename += 'labels_families_high_confidence_suggestions.png'
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()

    def createOutputDirectories(self):
        self.output_directory  = self.monitoring.iteration_dir
        self.output_directory += 'suggestions_accuracy/'
        dir_tools.createDirectory(self.output_directory)
        if self.monitoring.iteration_number == 1:
            output_directory  = self.monitoring.AL_directory
            output_directory += 'suggestions_accuracy/'
            dir_tools.createDirectory(output_directory)
