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
import numpy as np

from SecuML.Data.Instances import Instances

from SecuML.Plots.PlotDataset import PlotDataset
from SecuML.Plots.BoxPlot import BoxPlot
from SecuML.Plots.BarPlot import BarPlot
from SecuML.Plots.Density import Density

from SecuML.Tools import colors_tools
from SecuML.Tools import dir_tools

class DescriptiveStatistics(object):

    def __init__(self, experiment):
        self.instances = Instances()
        self.instances.initFromExperiment(experiment)
        self.output_directory = dir_tools.getExperimentOutputDirectory(experiment)

    # The file features_types.csv contains the list of features with their corresponding type (numeric or binary).
    # This file is updated after the processing of each feature to allow the user to display the results.
    # The features are sorted alphabetically.
    def generateDescriptiveStatistics(self):
        features_types = {}
        features_types['features'] = []
        features_types['types'] = {}
        for feature in self.instances.features_names:
            stats = FeatureDescriptiveStatistics(self.instances, feature, self.output_directory)
            stats.generateDescriptiveStatistics()
            features_types['features'].append(feature)
            features_types['features'].sort()
            features_types['types'][feature] = stats.feature_type
            with open(self.output_directory + 'features_types.json', 'w') as f:
                json.dump(features_types, f, indent = 2)

class FeatureDescriptiveStatistics(object):

    def __init__(self, instances, feature, output_directory):
        self.feature = feature
        self.output_directory = output_directory + self.feature + '/'
        dir_tools.createDirectory(self.output_directory)
        self.generatePlotDatasets(instances)
        self.setFeatureType()

    def generatePlotDatasets(self, instances):
        self.plot_datasets = {}
        self.plot_datasets['all'] = PlotDataset(instances.getFeatureValues(self.feature), 'all')
        self.plot_datasets['all'].setColor(colors_tools.getLabelColor('all'))
        if instances.hasTrueLabels():
            malicious_instances = instances.getInstancesFromIds(instances.getMaliciousIds(true_labels = True))
            malicious_dataset = PlotDataset(malicious_instances.getFeatureValues(self.feature), 'malicious')
            malicious_dataset.setColor(colors_tools.getLabelColor('malicious'))
            self.plot_datasets['malicious'] = malicious_dataset
            benign_instances = instances.getInstancesFromIds(instances.getBenignIds(true_labels = True))
            benign_dataset = PlotDataset(benign_instances.getFeatureValues(self.feature), 'benign')
            benign_dataset.setColor(colors_tools.getLabelColor('benign'))
            self.plot_datasets['benign'] = benign_dataset

    def setFeatureType(self):
        values = self.plot_datasets['all'].values
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
        for label, dataset in self.plot_datasets.iteritems():
            stats[label] = {
                    'min': np.amin(dataset.values),
                    'max': np.amax(dataset.values),
                    'mean': np.mean(dataset.values),
                    'std': np.std(dataset.values),
                    'median': np.median(dataset.values),
                    }
        with open(self.output_directory + 'stats.json', 'w') as f:
            json.dump(stats, f, indent = 2)

    def generateBoxplot(self):
        boxplot = BoxPlot(title = 'Feature ' + self.feature)
        for label, dataset in self.plot_datasets.iteritems():
            boxplot.addDataset(dataset)
        output_filename = self.output_directory + 'boxplot.png'
        boxplot.display(output_filename)
        return

    def generateHistogram(self):
        # 10 equal-width bins computed on all the data
        hist, bin_edges = np.histogram(self.plot_datasets['all'].values, bins = 10, density = False)
        x_labels = [str(bin_edges[e]) + ' - ' + str(bin_edges[e+1]) for e in range(len(bin_edges)-1)]
        barplot = BarPlot(x_labels)
        barplot.addDataset(hist, self.plot_datasets['all'].color, self.plot_datasets['all'].label)
        for label, dataset in self.plot_datasets.iteritems():
            if label == 'all':
                continue
            hist, bin_edges = np.histogram(dataset.values, bins = bin_edges, density = False)
            barplot.addDataset(hist, dataset.color, dataset.label)
        output_filename = self.output_directory + 'histogram.json'
        with open(output_filename, 'w') as f:
            barplot.display(f)

    def generateBinaryHistogram(self):
        barplot = BarPlot(['0', '1'])
        for label, dataset in self.plot_datasets.iteritems():
            num_0 = sum(dataset.values == 0)
            num_1 = sum(dataset.values == 1)
            barplot.addDataset([num_0, num_1], dataset.color, dataset.label)
        output_filename = self.output_directory + 'binary_histogram.json'
        with open(output_filename, 'w') as f:
            barplot.display(f)

    def generateDensity(self):
        density = Density(num_points = 200, bandwidth = 0.3, title = 'Feature ' + self.feature)
        for label, dataset in self.plot_datasets.iteritems():
            density.addDataset(dataset)
        output_filename = self.output_directory + 'density.png'
        density.display(output_filename)
