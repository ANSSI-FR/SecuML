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

from copy import deepcopy

from secuml.core.data.ids import Ids
from secuml.core.data.predictions import Predictions
from .proba_barplot import ProbaBarplot


class PredictionsMonitoring(object):

    def __init__(self):
        self.predictions = None
        self.proba_barplot = None

    def add_fold(self, predictions):
        if self.predictions is None:
            ids = Ids(deepcopy(predictions.ids.ids),
                      deepcopy(predictions.ids.idents),
                      deepcopy(predictions.ids.timestamps))
            self.predictions = Predictions(deepcopy(predictions.values), ids,
                                           predictions.info.multiclass,
                                           deepcopy(predictions.all_probas),
                                           deepcopy(predictions.probas),
                                           deepcopy(predictions.scores),
                                           deepcopy(predictions.ground_truth))
        else:
            self.predictions.union(predictions)

    def final_computations(self):
        # PredictionsBarplots only for probabilist binary models
        pred_info = self.predictions.info
        if not pred_info.multiclass and pred_info.with_probas:
            self.proba_barplot = ProbaBarplot(pred_info.with_ground_truth)
            self.proba_barplot.add_fold(self.predictions)

    def display(self, directory):
        if self.proba_barplot is not None:
            self.proba_barplot.display(directory)
