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
import numpy as np
import random

from secuml.core.data.ids import Ids
from secuml.core.data.labels_tools import label_bool_to_str
from secuml.core.tools.core_exceptions import SecuMLcoreException


class InconsistentPredictions(SecuMLcoreException):

    def __str__(self):
        return 'Inconsistent predictions.'


class InvalidPredictions(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class PredictionsInfo(object):

    def __init__(self, multiclass, predictions):
        self.multiclass = multiclass
        self.with_probas = predictions._with_probas()
        self.with_scores = predictions._with_scores()
        self.with_ground_truth = predictions._with_ground_truth()

    def equal(self, predictions_info):
        return (self.multiclass == predictions_info.multiclass and
                self.with_probas == predictions_info.with_probas and
                self.with_scores == predictions_info.with_scores and
                self.with_ground_truth == predictions_info.with_ground_truth)


class Prediction(object):

    def __init__(self, value, all_probas, proba, score, rank, instance_id,
                 multiclass, ground_truth=None):
        self.value = value
        self.all_probas = all_probas
        self.proba = proba
        self.score = score
        self.rank = rank
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
                 all_scores=None, scores=None, ground_truth=None):
        self.values = values
        self.ids = ids
        self.all_probas = self._get_ndarray(all_probas)
        self.probas = self._get_nparray(probas)
        self.all_scores = self._get_ndarray(all_scores)
        self.scores = self._get_nparray(scores)
        self.ground_truth = self._get_array(ground_truth)
        self._check_validity()
        self.info = PredictionsInfo(multiclass, self)
        self._set_ranking()

    def num_instances(self):
        return self.ids.num_instances()

    def get_alerts(self, threshold):
        if threshold is None or not self.info.with_probas:
            return [self.get_prediction_from_index(i[0])
                    for i, value in np.ndenumerate(self.values) if value]
        else:
            return [self.get_prediction_from_index(i[0])
                    for i, proba in np.ndenumerate(self.probas)
                    if proba > threshold]

    def union(self, predictions):
        if self.info.multiclass != predictions.info.multiclass:
            raise InvalidPredictions('Predictions with multiclass and binary '
                                     'values cannot be concatenated.')
        self.values = np.hstack((self.values, predictions.values))
        self.ids.union(predictions.ids)
        self.all_probas = np.vstack((self.all_probas, predictions.all_probas))
        self.probas = np.hstack((self.probas, predictions.probas))
        self.all_scores = np.vstack((self.all_scores, predictions.all_scores))
        self.scores = np.hstack((self.scores, predictions.scores))
        self.ground_truth.extend(predictions.ground_truth)
        self._set_ranking()

    def _set_ranking(self):
        def _rank_elems(values):
            arg_sort = np.argsort(-values)
            ranking = np.zeros(arg_sort.shape)
            for i, v in enumerate(arg_sort):
                ranking[v] = i
            return ranking
        if self.info.with_probas:
            self.ranking = _rank_elems(self.probas)
        elif self.info.with_scores:
            self.ranking = _rank_elems(self.scores)
        else:
            self.ranking = [None for _ in range(self.num_instances())]

    def get_prediction(self, instance_id):
        return self.get_prediction_from_index(self.ids.get_index(instance_id))

    def get_prediction_from_index(self, index):
        return Prediction(self.values[index],
                          self.all_probas[index],
                          self.probas[index],
                          self.scores[index],
                          self.ranking[index],
                          self.ids.ids[index],
                          self.info.multiclass,
                          ground_truth=self.ground_truth[index])

    def get_from_ids(self, instance_ids):
        return [self.get_prediction(i) for i in instance_ids]

    def get_within_range(self, proba_min, proba_max):
        return [self.get_prediction_from_index(i[0])
                for i, proba in np.ndenumerate(self.probas)
                if proba > proba_min and proba >= proba_max]

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

    @staticmethod
    def deepcopy(predictions):
        return Predictions(deepcopy(predictions.values),
                           Ids.deepcopy(predictions.ids),
                           predictions.info.multiclass,
                           all_probas=deepcopy(predictions.all_probas),
                           probas=deepcopy(predictions.probas),
                           all_scores=deepcopy(predictions.all_scores),
                           scores=deepcopy(predictions.scores),
                           ground_truth=deepcopy(predictions.ground_truth))

    def _check_validity(self):
        num_instances = self.num_instances()
        if len(self.values) != num_instances:
            raise InvalidPredictions('There are %d instances '
                                     'but %d values are provided.'
                                     % (num_instances, len(self.values)))
        elif self.all_probas.shape[0] != num_instances:
            raise InvalidPredictions('There are %d instances '
                                     'but %d arrays of probabilities '
                                     'are provided.'
                                     % (num_instances,
                                        self.all_probas.shape[0]))
        elif self.probas.shape[0] != num_instances:
            raise InvalidPredictions('There are %d instances '
                                     'but %d probabilities are provided.'
                                     % (num_instances, self.probas.shape[0]))
        elif self.all_scores.shape[0] != num_instances:
            raise InvalidPredictions('There are %d instances '
                                     'but %d arrays of scores are provided.'
                                     % (num_instances, self.scores.shape[0]))
        elif self.scores.shape[0] != num_instances:
            raise InvalidPredictions('There are %d instances '
                                     'but %d scores are provided.'
                                     % (num_instances, self.scores.shape[0]))
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

    def _with_probas(self):
        return all(l is not None for l in self.probas)

    def _with_scores(self):
        return all(l is not None for l in self.scores)

    def _with_ground_truth(self):
        return all(l is not None for l in self.ground_truth)
