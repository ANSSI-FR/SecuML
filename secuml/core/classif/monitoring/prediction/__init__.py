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
import pandas as pd
import os.path as path

from secuml.core.tools.matrix import sort_data_frame
from .proba_barplot import ProbaBarplot


class PredictionsMonitoring(object):

    def __init__(self, conf, has_ground_truth):
        self.conf = conf
        self.has_ground_truth = has_ground_truth
        self.predictions = None
        self.all_predicted_proba = None
        # PredictionsBarplots only for probabilist binary models
        if not self.conf.multiclass and self.conf.is_probabilist():
            self.proba_barplot = ProbaBarplot(self.has_ground_truth)
        else:
            self.proba_barplot = None

    def add_fold(self, predictions):
        if self.proba_barplot is not None:
            self.proba_barplot.add_fold(predictions)
        columns = ['predicted_proba', 'predictions', 'ground_truth', 'scores']
        fold_predictions = pd.DataFrame(np.zeros((predictions.num_instances(),
                                                  len(columns))),
                                        index=predictions.ids.ids,
                                        columns=columns)
        fold_predictions['predicted_proba'] = predictions.probas
        fold_predictions['predictions'] = predictions.values
        fold_predictions['ground_truth'] = predictions.ground_truth
        fold_predictions['scores'] = predictions.scores
        if self.predictions is None:
            self.predictions = fold_predictions
        else:
            self.predictions = pd.concat([self.predictions, fold_predictions])

    def final_computations(self):
        sort_data_frame(self.predictions, 'predicted_proba', True, True)

    def display(self, directory):
        # TODO a mettre dans la base de donnees.
        with open(path.join(directory, 'predictions.csv'), 'w') as f:
            self.predictions.to_csv(f, index_label='instance_id')
        if self.proba_barplot is not None:
            self.proba_barplot.display(directory)
