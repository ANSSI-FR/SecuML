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

from secuml.core.data.predictions import Predictions
from secuml.core.tools.core_exceptions import SecuMLcoreException
from .proba_barplot import ProbaBarplot
from .pred_barplot import PredictionBarplot
from .score_barplot import ScoreBarplot


class AddTooManyFolds(SecuMLcoreException):
    pass


class FoldsNotAdded(SecuMLcoreException):
    pass


class PredictionsMonitoring(object):

    def __init__(self, logger, num_folds):
        self.logger = logger
        self.num_folds = num_folds
        self.predictions = None
        self.barplot = None
        self.num_added_folds = 0

    def add_fold(self, predictions):
        self.num_added_folds += 1
        if self.num_added_folds > self.num_folds:
            raise AddTooManyFolds()
        if self.predictions is None:
            if self.num_folds > 1:
                self.predictions = Predictions.deepcopy(predictions)
            else:
                self.predictions = predictions
        else:
            self.predictions.union(predictions)

    def final_computations(self):
        if self.num_folds != self.num_added_folds:
            raise FoldsNotAdded()
        pred_info = self.predictions.info
        if not pred_info.multiclass and pred_info.with_probas:
            self.barplot = ProbaBarplot(pred_info.with_ground_truth)
        elif not pred_info.multiclass and pred_info.with_scores:
            self.barplot = ScoreBarplot(pred_info.with_ground_truth,
                                        self.logger)
        else:
            self.barplot = PredictionBarplot(pred_info.with_ground_truth)
        self.barplot.set_predictions(self.predictions)

    def display(self, directory):
        self.barplot.display(directory)
