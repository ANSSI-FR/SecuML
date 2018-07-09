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

from SecuML.core.Tools import matrix_tools
from .PredictionsBarplots import PredictionsBarplots


class PredictionsMonitoring(object):

    def __init__(self, conf, has_ground_truth):
        self.conf = conf
        self.has_ground_truth = has_ground_truth
        self.predictions = None
        self.all_predicted_proba = None
        # PredictionsBarplots only for probabilist binary models
        if not self.conf.families_supervision and self.conf.probabilistModel():
            self.predictions_barplots = PredictionsBarplots(
                self.has_ground_truth)
        else:
            self.predictions_barplots = None

    def addFold(self, predictions):
        if self.predictions_barplots is not None:
            self.predictions_barplots.addFold(predictions)
        columns = ['predicted_proba', 'predictions', 'ground_truth', 'scores']
        fold_predictions = pd.DataFrame(
            np.zeros((predictions.numInstances(), len(columns))),
            index=predictions.ids.ids,
            columns=columns)
        fold_predictions['predicted_proba'] = predictions.predicted_proba
        fold_predictions['predictions'] = predictions.predictions
        fold_predictions['ground_truth'] = predictions.ground_truth
        fold_predictions['scores'] = predictions.predicted_scores
        if self.all_predicted_proba is None:
            self.all_predicted_proba = predictions.all_predicted_proba
        else:
            self.all_predicted_proba = np.vstack((self.all_predicted_proba[0],
                                                  predictions.all_predicted_proba))
        if self.predictions is None:
            self.predictions = fold_predictions
        else:
            self.predictions = pd.concat([self.predictions, fold_predictions])

    def finalComputations(self):
        matrix_tools.sortDataFrame(
            self.predictions, 'predicted_proba', True, True)

    def display(self, directory):
        with open(path.join(directory, 'predictions.csv'), 'w') as f:
            self.predictions.to_csv(f, index_label='instance_id')
        if self.predictions_barplots is not None:
            self.predictions_barplots.display(directory)

    def getPredictedLabels(self):
        return list(self.predictions.loc[:, 'predictions'])

    def getAllPredictedProba(self):
        return self.all_predicted_proba

    def getPredictedProbas(self):
        return list(self.predictions['predicted_proba'])
