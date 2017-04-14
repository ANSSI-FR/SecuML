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

import numpy as np
import pandas as pd

from SecuML.Tools import matrix_tools
from PredictionsBarplots import PredictionsBarplots

class PredictionsMonitoring(object):

    def __init__(self, conf):
        self.conf = conf
        # PredictionsBarplots only for probabilist binary models
        if not self.conf.families_supervision and self.conf.probabilistModel():
            self.predictions_barplots = PredictionsBarplots()
        else:
            self.predictions_barplots = None
        self.predicted_proba_all = None
        self.predictions = None

    def addFold(self, instances_ids, predicted_proba_all, predicted_proba, predicted_scores, predicted_labels, true_labels):
        if self.predictions_barplots is not None:
            self.predictions_barplots.addFold(instances_ids, predicted_proba, true_labels)
        fold_predictions = pd.DataFrame(
                np.zeros((len(instances_ids), 4)),
                index = instances_ids,
                columns = ['predicted_proba', 'predicted_labels', 'true_labels', 'scores'])
        fold_predictions['predicted_proba'] = predicted_proba
        fold_predictions['predicted_labels'] = predicted_labels
        fold_predictions['true_labels'] = true_labels
        fold_predictions['scores'] = predicted_scores

        if self.predicted_proba_all is None:
            self.predicted_proba_all = predicted_proba_all
        else:
            self.predicted_proba_all = np.concatenate(self.predicted_proba_all, predicted_proba_all)

        if self.predictions is None:
            self.predictions = fold_predictions
        else:
            self.predictions = pd.concat([self.predictions, fold_predictions])

    def finalComputations(self):
        matrix_tools.sortDataFrame(self.predictions, 'predicted_proba', True, True)

    def display(self, directory):
        with open(directory + 'predictions.csv', 'w') as f:
            self.predictions.to_csv(f, index_label = 'instance_id')
        if self.predictions_barplots is not None:
            self.predictions_barplots.display(directory)

    def getPredictedLabels(self):
        return list(self.predictions.loc[:,'predicted_labels'])

    def getAllPredictedProba(self):
        return self.predicted_proba_all
