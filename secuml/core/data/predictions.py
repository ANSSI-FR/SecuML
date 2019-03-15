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

from secuml.core.tools.core_exceptions import SecuMLcoreException


class InvalidPredictions(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Prediction(object):

    def __init__(self, value, all_probas, proba, score, instance_id,
                 ground_truth=None):
        self.value = value
        self.all_probas = all_probas
        self.proba = proba
        self.score = score
        self.instance_id = instance_id
        self.ground_truth = ground_truth


class Predictions(object):

    def __init__(self, values, all_probas, probas, scores, ids,
                 ground_truth=None):
        self.values = values
        self.all_probas = all_probas
        self.probas = probas
        self.scores = scores
        self.ids = ids
        if ground_truth is not None:
            self.ground_truth = ground_truth
        else:
            self.ground_truth = [None for _ in range(self.ids.num_instances())]
        self.check_validity()

    def num_instances(self):
        return self.ids.num_instances()

    def get_prediction(self, instance_id):
        return self.get_prediction_from_index(self.ids.get_index(instance_id))

    def get_prediction_from_index(self, index):
        return Prediction(self.values[index],
                          self.all_probas[index],
                          self.probas[index],
                          self.scores[index],
                          self.ids.ids[index],
                          self.ground_truth[index])

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

    def check_validity(self):
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
