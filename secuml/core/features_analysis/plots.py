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

import numpy as np
import os
import os.path as path

from secuml.core.data.labels_tools import BENIGN, MALICIOUS
from secuml.core.data.features import FeatureType
from secuml.core.tools.color import get_label_color
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.core.tools.plots.boxplot import BoxPlot
from secuml.core.tools.plots.barplot import BarPlot
from secuml.core.tools.plots.density import Density


class FeaturePlots(object):

    def __init__(self, instances, feature_index):
        self.feature_index = feature_index
        features_info = instances.features.info
        self.feature_type = features_info.types[self.feature_index]
        self.feature_name = features_info.names[self.feature_index]
        self.feature_id = features_info.ids[self.feature_index]
        self.all_values = instances.features.get_values_from_index(
                                                            self.feature_index)
        self._gen_plot_datasets(instances)

    def compute(self):
        if self.feature_type == FeatureType.binary:
            self._gen_binary_histogram()
        elif self.feature_type == FeatureType.numeric:
            self._gen_bloxplot()
            # Added to deal with numpy issue #8627
            # In this case, the variance is null.
            # The plots are not generated, since the scoring metrics
            # contain all the informations.
            try:
                self._gen_histogram()
            except:
                self.barplot = None
                pass
            self._gen_density()

    def export(self, output_dir):
        output_dir = path.join(output_dir, str(self.feature_id))
        os.makedirs(output_dir)
        if self.barplot is None:
            return
        if self.feature_type == FeatureType.binary:
            self.barplot.export_to_json(path.join(output_dir,
                                                  'binary_histogram.json'))
        elif self.feature_type == FeatureType.numeric:
            self.boxplot.display(path.join(output_dir, 'boxplot.png'))
            self.barplot.export_to_json(path.join(output_dir, 'histogram.json'))
            self.density.display(path.join(output_dir, 'density.png'))

    def _gen_plot_datasets(self, instances):
        self.plot_datasets = {}
        self._gen_label_plot_dataset(instances, MALICIOUS)
        self._gen_label_plot_dataset(instances, BENIGN)
        self._gen_label_plot_dataset(instances, 'unlabeled')

    def _gen_label_plot_dataset(self, instances, label):
        if label != 'unlabeled':
            instances = instances.get_annotated_instances(label=label)
        else:
            instances = instances.get_unlabeled_instances()
        values = instances.features.get_values_from_index(self.feature_index)
        dataset = PlotDataset(values, label)
        dataset.set_color(get_label_color(label))
        self.plot_datasets[label] = dataset

    def _gen_bloxplot(self):
        self.boxplot = BoxPlot(title='Feature %s' % self.feature_name)
        for label, dataset in self.plot_datasets.items():
            if len(dataset.values) > 0:
                self.boxplot.add_dataset(dataset)

    def _gen_histogram(self):
        # 10 equal-width bins computed on all the data
        _, bin_edges = np.histogram(self.all_values, bins=10, density=False)
        x_labels = ['%.2f - %.2f' % (bin_edges[e], bin_edges[e+1])
                    for e in range(len(bin_edges) - 1)]
        self.barplot = BarPlot(x_labels)
        for label, dataset in self.plot_datasets.items():
            if len(dataset.values) > 0:
                hist, _ = np.histogram(dataset.values, bins=bin_edges,
                                       density=False)
                hist_dataset = PlotDataset(hist, label)
                hist_dataset.set_color(dataset.color)
                self.barplot.add_dataset(hist_dataset)

    def _gen_binary_histogram(self):
        self.barplot = BarPlot(['0', '1'])
        for label, dataset in self.plot_datasets.items():
            if len(dataset.values) > 0:
                num_0 = sum(dataset.values == 0)
                num_1 = sum(dataset.values == 1)
                hist_dataset = PlotDataset([num_0, num_1], label)
                hist_dataset.set_color(dataset.color)
                self.barplot.add_dataset(hist_dataset)

    def _gen_density(self):
        self.density = Density(title='Feature %s' % self.feature_name)
        for _, dataset in self.plot_datasets.items():
            if len(dataset.values) > 0:
                self.density.add_dataset(dataset)
