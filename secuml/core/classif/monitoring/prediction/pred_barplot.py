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

from secuml.core.data.labels_tools import label_bool_to_str
from secuml.core.data.predictions import InconsistentPredictions
from secuml.core.tools.plots.barplot import BarPlot
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.core.tools.color import get_error_color


class PredictionBarplot(object):

    def __init__(self, has_ground_truth):
        self.predictions = {}
        self.multiclass = None
        self.has_ground_truth = has_ground_truth

    def set_predictions(self, predictions):
        if self.multiclass is None:
            self.multiclass = predictions.info.multiclass
        elif self.multiclass != predictions.info.multiclass:
            raise InconsistentPredictions()
        for instance_id, prediction, label in zip(predictions.ids.ids,
                                                  predictions.values,
                                                  predictions.ground_truth):
            if prediction not in self.predictions:
                self.predictions[prediction] = []
            self.predictions[prediction].append({'instance_id': instance_id,
                                                 'ground_truth_label': label})

    # error: None  -> display all instances
    #        True  -> display wrong predictions
    #        False -> display right predictions
    def _display(self, barplot, labels, error=None):
        if error is not None:
            values = [len([p for p in self.predictions[l]
                           if (p['ground_truth_label'] == l) != error])
                      for l in labels]
            label = 'wrong predictions' if error else 'right predictions'
        else:
            values = [len(self.predictions[l]) for l in labels]
            label = 'all'
        dataset = PlotDataset(np.array(values), label)
        dataset.set_color(get_error_color(error))
        barplot.add_dataset(dataset)

    def display(self, directory):
        labels = list(self.predictions.keys())
        if self.multiclass:
            xlabels = labels
        else:
            xlabels = [label_bool_to_str(l) for l in labels]
        barplot = BarPlot(xlabels)
        if not self.has_ground_truth:
            self._display(barplot, labels)
        else:
            self._display(barplot, labels, error=False)
            self._display(barplot, labels, error=True)
        barplot.export_to_json(path.join(directory, 'pred_barplot.json'))
