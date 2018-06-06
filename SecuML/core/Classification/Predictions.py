# SecuML
# Copyright (C) 2018  ANSSI
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


class InvalidPredictions(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Predictions(object):

    def __init__(self, predictions, all_predicted_proba,
                 predicted_proba, predicted_scores,
                 ids, ground_truth=None):
        self.predictions = predictions
        self.all_predicted_proba = all_predicted_proba
        self.predicted_proba = predicted_proba
        self.predicted_scores = predicted_scores
        self.ids = ids
        if ground_truth is not None:
            self.ground_truth = ground_truth
        else:
            self.ground_truth = [None for i in range(self.ids.numInstances())]
        self.checkValidity()

    def numInstances(self):
        return self.ids.numInstances()

    def setGroundTruth(self, ground_truth):
        num_instances = self.numInstances()
        if len(self.ground_truth) != num_instances:
            message = 'There are ' + str(num_instances) + ' instances '
            message += 'but ' + str(len(self.ground_truth)) + \
                'ground-truth annotations are provided.'
            raise InvalidPredictions(message)
        self.ground_truth = ground_truth

    def checkValidity(self):
        message = None
        num_instances = self.numInstances()
        if len(self.predictions) != num_instances:
            message = 'There are ' + str(num_instances) + ' instances '
            message += 'but ' + str(len(self.predictions)) + \
                ' predictions are provided.'
        elif len(self.all_predicted_proba) != num_instances:
            message = 'There are ' + str(num_instances) + ' instances '
            message += 'but ' + str(len(self.predictions)) + \
                ' arrays of probabilities are provided.'
        elif len(self.predicted_proba) != num_instances:
            message = 'There are ' + str(num_instances) + ' instances '
            message += 'but ' + str(len(self.predicted_proba)) + \
                ' probabilities are provided.'
        elif len(self.predicted_scores) != num_instances:
            message = 'There are ' + str(num_instances) + ' instances '
            message += 'but ' + \
                str(len(self.predicted_scores)) + ' scores are provided.'
        elif len(self.ground_truth) != num_instances:
            message = 'There are ' + str(num_instances) + ' instances '
            message += 'but ' + str(len(self.ground_truth)) + \
                'ground-truth annotations are provided.'
        if message is not None:
            raise InvalidPredictions(message)
