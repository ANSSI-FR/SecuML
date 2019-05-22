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

import numpy as np
import os
import os.path as path
from scipy.sparse.base import spmatrix

from secuml.core.data.labels_tools import BENIGN, MALICIOUS
from secuml.core.data.features import FeatureType
from secuml.core.tools.color import get_label_color
from secuml.core.tools.color import colors
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.core.tools.plots.boxplot import BoxPlot
from secuml.core.tools.plots.barplot import BarPlot
from secuml.core.tools.plots.density import Density
from secuml.core.tools.plots.histogram import Histogram


class FeaturePlots(object):

    def __init__(self, instances, multiclass, feature_index, logger,
                 with_density=True):
        self.feature_index = feature_index
        self.logger = logger
        self.with_density = with_density
        features_info = instances.features.info
        self.feature_type = features_info.types[self.feature_index]
        self.feature_name = features_info.names[self.feature_index]
        self.feature_id = features_info.ids[self.feature_index]
        self._gen_plot_datasets(instances, multiclass)

    def compute(self):
        if self.feature_type == FeatureType.binary:
            self._gen_binary_histogram()
        elif self.feature_type == FeatureType.numeric:
            self._gen_bloxplot()
            self._gen_histogram()
            if self.with_density:
                self._gen_density()

    def export(self, output_dir):
        output_dir = path.join(output_dir, str(self.feature_id))
        os.makedirs(output_dir)
        if self.feature_type == FeatureType.binary:
            self.barplot.export_to_json(path.join(output_dir,
                                                  'binary_histogram.json'))
        elif self.feature_type == FeatureType.numeric:
            self.boxplot.display(path.join(output_dir, 'boxplot.png'))
            self.barplot.export_to_json(path.join(output_dir,
                                                  'histogram.json'))
            if self.with_density:
                self.density.display(path.join(output_dir, 'density.png'))

    def _gen_plot_datasets(self, instances, multiclass):
        self.plot_datasets = {}
        if not multiclass:
            self._gen_label_plot_dataset(instances, label=MALICIOUS)
            self._gen_label_plot_dataset(instances, label=BENIGN)
            self._gen_label_plot_dataset(instances, label='unlabeled')
        else:
            families = list(instances.annotations.get_families_values())
            families_colors = colors(len(families))
            for family, color in zip(families, families_colors):
                self._gen_label_plot_dataset(instances, family=family,
                                             color=color)

    def _gen_label_plot_dataset(self, instances, label=None, family=None,
                                color=None):
        if label is not None:
            if label != 'unlabeled':
                instances = instances.get_annotated_instances(label=label)
            else:
                instances = instances.get_unlabeled_instances()
        else:
            instances = instances.get_annotated_instances(family=family)
        values = instances.features.get_values_from_index(self.feature_index)
        if isinstance(values, spmatrix):
            values = values.toarray()
        plot_label = label if label is not None else family
        plot_color = color
        if plot_color is None:
            plot_color = get_label_color(plot_label)
        dataset = PlotDataset(values, plot_label)
        dataset.set_color(plot_color)
        self.plot_datasets[plot_label] = dataset

    def _gen_bloxplot(self):
        self.boxplot = BoxPlot(title='Feature %s' % self.feature_name)
        for label, dataset in self.plot_datasets.items():
            if dataset.values.shape[0] > 0:
                self.boxplot.add_dataset(dataset)

    def _gen_histogram(self):
        self.barplot = Histogram(self.plot_datasets, self.logger)

    def _gen_binary_histogram(self):
        self.barplot = BarPlot(['0', '1'])
        for label, dataset in self.plot_datasets.items():
            if dataset.values.shape[0] > 0:
                num_0 = sum(dataset.values == 0)
                num_1 = sum(dataset.values == 1)
                hist_dataset = PlotDataset(np.array([num_0, num_1]), label)
                hist_dataset.set_color(dataset.color)
                self.barplot.add_dataset(hist_dataset)

    def _gen_density(self):
        self.density = Density(title='Feature %s' % self.feature_name)
        for _, dataset in self.plot_datasets.items():
            if dataset.values.shape[0] > 0:
                self.density.add_dataset(dataset)
