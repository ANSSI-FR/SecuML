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
import os.path as path

from secuml.core.data.labels_tools import BENIGN, MALICIOUS
from secuml.core.data.labels_tools import label_str_to_bool
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.core.tools.plots.histogram import Histogram


class ScoreBarplot(object):

    def __init__(self, has_ground_truth, logger):
        self.has_ground_truth = has_ground_truth
        self.logger = logger
        self.predictions = None
        self.datasets = None

    def set_predictions(self, predictions):
        self.predictions = predictions
        self.datasets = {}
        if not self.has_ground_truth:
            self.datasets['all'] = PlotDataset(predictions.scores, 'all')
        else:
            for label in [MALICIOUS, BENIGN]:
                label_bool = label_str_to_bool(label)
                scores = [predictions.scores[i]
                          for i in range(predictions.num_instances())
                          if predictions.ground_truth[i] == label_bool]
                self.datasets[label] = PlotDataset(np.array(scores), label)

    def display(self, directory):
        barplot = Histogram(self.datasets, self.logger)
        barplot.export_to_json(path.join(directory, 'pred_barplot.json'))
