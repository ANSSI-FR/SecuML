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
import random

from secuml.core.data.labels_tools import label_bool_to_str
from secuml.core.tools.core_exceptions import SecuMLcoreException


class InvalidPredictions(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Prediction(object):

    def __init__(self, value, all_probas, proba, score, instance_id,
                 multiclass, ground_truth=None):
        self.value = value
        self.all_probas = all_probas
        self.proba = proba
        self.score = score
        self.instance_id = instance_id
        self.multiclass = multiclass
        self.ground_truth = ground_truth

    def value_to_str(self):
        if self.multiclass:
            return str(self.value)
        else:
            return label_bool_to_str(self.value)


class Predictions(object):

    def __init__(self, values, ids, multiclass, all_probas=None, probas=None,
                 scores=None, ground_truth=None):
        self.values = values
        self.ids = ids
        self.multiclass = multiclass
        self.all_probas = self._get_ndarray(all_probas)
        self.probas = self._get_nparray(probas)
        self.scores = self._get_nparray(scores)
        self.ground_truth = self._get_array(ground_truth)
        self._check_validity()

    def with_proba(self):
        return all(l is not None for l in self.probas)

    def num_instances(self):
        return self.ids.num_instances()

    def get_alerts(self, threshold):
        if threshold is None or not self.with_proba():
            return [self.get_prediction_from_index(i[0])
                    for i, value in np.ndenumerate(self.values) if value]
        else:
            return [self.get_prediction_from_index(i[0])
                    for i, proba in np.ndenumerate(self.probas)
                    if proba > threshold]

    def union(self, predictions):
        if self.multiclass != predictions.multiclass:
            raise InvalidPredictions('Predictions with multiclass and binary '
                                     'values cannot be concatenated.')
        self.values.extend(predictions.values)
        self.ids.union(predictions.ids)
        self.all_probas = np.vstack((self.all_probas, predictions.all_probas))
        self.probas = np.hstack((self.probas, predictions.probas))
        if self.info.multiclass:
            self.scores = np.vstack((self.scores, predictions.scores))
        else:
            self.scores = np.hstack((self.scores, predictions.scores))
        self.ground_truth.extend(predictions.ground_truth)

    def get_prediction(self, instance_id):
        return self.get_prediction_from_index(self.ids.get_index(instance_id))

    def get_prediction_from_index(self, index):
        return Prediction(self.values[index],
                          self.all_probas[index],
                          self.probas[index],
                          self.scores[index],
                          self.ids.ids[index],
                          self.multiclass,
                          ground_truth=self.ground_truth[index])

    def get_from_ids(self, instance_ids):
        return [self.get_prediction(i) for i in instance_ids]

    def get_within_range(self, proba_min, proba_max):
        selection = []
        for i, proba in np.ndenumerate(self.probas):
            if proba > proba_min and proba <= proba_max:
                selection.append(self.get_prediction_from_index(i[0]))
        return selection

    def to_list(self):
        return [self.get_prediction_from_index(i)
                for i in range(self.num_instances())]

    def get_random(self, batch, drop_instances):
        selected_ids = [i for i in self.ids.ids if i not in drop_instances]
        if batch < self.num_instances():
            selected_ids = random.sample(selected_ids, batch)
        return self.get_from_ids(selected_ids)

    def set_ground_truth(self, ground_truth):
        num_instances = self.num_instances()
        if len(self.ground_truth) != num_instances:
            raise InvalidPredictions(
                    'There are %d instances '
                    'but %d ground-truth annotations are provided'
                    % (num_instances, len(self.ground_truth)))
        self.ground_truth = ground_truth

    def _check_validity(self):
        num_instances = self.num_instances()
        if len(self.values) != num_instances:
            raise InvalidPredictions('There are %d instances '
                                     'but %d values are provided.'
                                     % (num_instances, len(self.values)))
        elif len(self.all_probas) != num_instances:
            raise InvalidPredictions('There are %d instances '
                                     'but %d arrays of probabilities '
                                     'are provided.'
                                     % (num_instances, len(self.all_probas)))
        elif len(self.probas) != num_instances:
            raise InvalidPredictions('There are %d instances '
                                     'but %d probabilities are provided.'
                                     % (num_instances, len(self.probas)))
        elif len(self.scores) != num_instances:
            raise InvalidPredictions('There are %d instances '
                                     'but %d scores are provided.'
                                     % (num_instances, len(self.scores)))
        elif len(self.ground_truth) != num_instances:
            raise InvalidPredictions('There are %d instances '
                                     'but %d ground-truth annotations '
                                     'are provided.'
                                     % (num_instances, len(self.ground_truth)))

    def _get_nparray(self, array):
        if array is None:
            return np.array(self._get_array(array))
        else:
            return array

    def _get_ndarray(self, array):
        if array is None:
            return np.ndarray((self.ids.num_instances(), 1),
                              buffer=np.array(self._get_array(array)))
        else:
            return array

    def _get_array(self, array):
        if array is None:
            return [None for _ in range(self.ids.num_instances())]
        else:
            return array
