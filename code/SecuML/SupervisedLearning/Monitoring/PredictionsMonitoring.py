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

from PredictionsBarplots import PredictionsBarplots

class PredictionsMonitoring(object):

    def __init__(self):
        self.predictions_barplots = PredictionsBarplots()
        self.predictions          = None

    def addFold(self, instances_ids, predicted_proba, predicted_scores, predicted_labels, true_labels):
        self.predictions_barplots.addFold(instances_ids, predicted_proba, true_labels)
        fold_predictions = pd.DataFrame(
                np.zeros((len(instances_ids), 4)),
                index = instances_ids,
                columns = ['predicted_proba', 'predicted_labels', 'true_labels', 'scores'])
        fold_predictions.loc[:, 'predicted_proba'] = predicted_proba
        fold_predictions.loc[:, 'predicted_labels'] = predicted_labels
        fold_predictions.loc[:, 'true_labels'] = true_labels
        fold_predictions.loc[:, 'scores'] = predicted_scores
        if self.predictions is None:
            self.predictions = fold_predictions
        else:
            self.predictions = pd.concat([self.predictions, fold_predictions])

    def finalComputations(self):
        if pd.__version__ in ['0.13.0', '0.14.1']:
            self.predictions.sort(['predicted_proba'],
                    ascending = [True], inplace = True)
        else:
            self.predictions.sort_values(['predicted_proba'],
                    ascending = [True], inplace = True)

    def display(self, directory):
        with open(directory + 'predictions.csv', 'w') as f:
            self.predictions.to_csv(f, index_label = 'instance_id')
        self.predictions_barplots.display(directory)

    def getPredictedLabels(self):
        return list(self.predictions.loc[:,'predicted_labels'])
