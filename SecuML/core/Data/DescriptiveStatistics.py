# SecuML
# Copyright (C) 2016-2017  ANSSI
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

import json
import numpy as np

from SecuML.core.Data import labels_tools

from SecuML.core.Tools.Plots.PlotDataset import PlotDataset
from SecuML.core.Tools.Plots.BoxPlot import BoxPlot
from SecuML.core.Tools.Plots.BarPlot import BarPlot
from SecuML.core.Tools.Plots.Density import Density

from SecuML.core.Tools import colors_tools
from SecuML.core.Tools import dir_tools


class DescriptiveStatistics(object):

    def __init__(self):
        return

    # The file features_types.csv contains the list of features with their corresponding type (numeric or binary).
    # This file is updated after the processing of each feature to allow the user to display the results.
    # The features are sorted alphabetically.
    def generateDescriptiveStatistics(self, instances, output_directory):
        features_types = {}
        features_types['features'] = []
        features_types['types'] = {}
        for feature in instances.features.getNames():
            stats = FeatureDescriptiveStatistics(
                instances, feature, output_directory)
            stats.generateDescriptiveStatistics()
            features_types['features'].append(feature)
            features_types['features'].sort()
            features_types['types'][feature] = stats.feature_type
            with open(output_directory + 'features_types.json', 'w') as f:
                json.dump(features_types, f, indent=2)


class FeatureDescriptiveStatistics(object):

    def __init__(self, instances, feature, output_directory):
        self.feature = feature
        self.output_directory = output_directory + self.feature + '/'
        dir_tools.createDirectory(self.output_directory)
        self.has_ground_truth = instances.hasGroundTruth()
        self.generatePlotDatasets(instances)
        self.setFeatureType()

    def generatePlotDatasets(self, instances):
        self.plot_datasets = {}
        if self.has_ground_truth:
            self.generateLabelPlotDatasets(instances, labels_tools.MALICIOUS)
            self.generateLabelPlotDatasets(instances, labels_tools.BENIGN)
        else:
            self.plot_datasets['all'] = PlotDataset(
                instances.features.getFeatureValues(self.feature), 'all')
            self.plot_datasets['all'].setColor(
                colors_tools.getLabelColor('all'))

    def generateLabelPlotDatasets(self, instances, label):
        instances = instances.getInstancesFromIds(
            instances.ground_truth.getAnnotatedIds(label))
        dataset = PlotDataset(instances.features.getFeatureValues(self.feature),
                              label)
        dataset.setColor(colors_tools.getLabelColor(label))
        self.plot_datasets[label] = dataset

    def setFeatureType(self):
        if not self.has_ground_truth:
            values = self.plot_datasets['all'].values
        else:
            values = self.plot_datasets[labels_tools.BENIGN].values
        if all(v in [0, 1] for v in values):
            self.feature_type = 'binary'
        else:
            self.feature_type = 'numeric'

    def generateDescriptiveStatistics(self):
        if self.feature_type == 'binary':
            self.generateBinaryHistogram()
        elif self.feature_type == 'numeric':
            self.generateStatistics()
            self.generateBoxplot()
            self.generateHistogram()
            self.generateDensity()

    def generateStatistics(self):
        stats = {}
        for label, dataset in self.plot_datasets.items():
            stats[label] = {
                'min': np.amin(dataset.values),
                'max': np.amax(dataset.values),
                'mean': np.mean(dataset.values),
                'std': np.std(dataset.values),
                'median': np.median(dataset.values),
            }
        with open(self.output_directory + 'stats.json', 'w') as f:
            json.dump(stats, f, indent=2)

    def generateBoxplot(self):
        boxplot = BoxPlot(title='Feature ' + self.feature)
        for label, dataset in self.plot_datasets.items():
            boxplot.addDataset(dataset)
        output_filename = self.output_directory + 'boxplot.png'
        boxplot.display(output_filename)
        return

    def generateHistogram(self):
        # 10 equal-width bins computed on all the data
        if not self.has_ground_truth:
            hist, bin_edges = np.histogram(
                self.plot_datasets['all'].values, bins=10, density=False)
        else:
            hist, bin_edges = np.histogram(
                self.plot_datasets[labels_tools.MALICIOUS].values, bins=10, density=False)
        x_labels = [str(bin_edges[e]) + ' - ' + str(bin_edges[e + 1])
                    for e in range(len(bin_edges) - 1)]
        barplot = BarPlot(x_labels)
        for label, dataset in self.plot_datasets.items():
            hist, bin_edges = np.histogram(
                dataset.values, bins=bin_edges, density=False)
            hist_dataset = PlotDataset(hist, dataset.label)
            hist_dataset.setColor(dataset.color)
            barplot.addDataset(hist_dataset)
        output_filename = self.output_directory + 'histogram.json'
        with open(output_filename, 'w') as f:
            barplot.exportJson(f)

    def generateBinaryHistogram(self):
        barplot = BarPlot(['0', '1'])
        for label, dataset in self.plot_datasets.items():
            num_0 = sum(dataset.values == 0)
            num_1 = sum(dataset.values == 1)
            hist_dataset = PlotDataset([num_0, num_1], dataset.label)
            hist_dataset.setColor(dataset.color)
            barplot.addDataset(hist_dataset)
        output_filename = self.output_directory + 'binary_histogram.json'
        with open(output_filename, 'w') as f:
            barplot.exportJson(f)

    def generateDensity(self):
        density = Density(num_points=200, bandwidth=0.3,
                          title='Feature ' + self.feature)
        for label, dataset in self.plot_datasets.items():
            density.addDataset(dataset)
        output_filename = self.output_directory + 'density.png'
        density.display(output_filename)
