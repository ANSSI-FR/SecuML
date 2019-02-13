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

import json
import numpy as np
from sklearn.metrics import confusion_matrix

# Stores a 2*2 matrix
# The rows correspond to the actual labels
# The columns correspond to the predicted labels
# index 0: Malicious
# index 1: Benign
#
# confusion_matrix[i,j] is is equal to the number
# of instances known to be in group i but predicted
# to be in group j.


class ConfusionMatrix(object):

    def __init__(self):
        self.confusion_matrix = np.zeros((2, 2))

    def add_fold(self, predictions):
        if predictions.num_instances() > 0:
            conf_matrix = confusion_matrix(predictions.ground_truth,
                                           predictions.values, [True, False])
            self.confusion_matrix += conf_matrix

    def get_true_positives(self):
        return self.confusion_matrix[0][0]

    def get_true_negatives(self):
        return self.confusion_matrix[1][1]

    def get_false_positives(self):
        return self.confusion_matrix[1][0]

    def get_false_negatives(self):
        return self.confusion_matrix[0][1]

    def to_json_object(self):
        confusion_matrix = {}
        confusion_matrix['TP'] = self.get_true_positives()
        confusion_matrix['TN'] = self.get_true_negatives()
        confusion_matrix['FP'] = self.get_false_positives()
        confusion_matrix['FN'] = self.get_false_negatives()
        return confusion_matrix

    def to_json(self, f):
        confusion_matrix = self.to_json_object()
        json.dump(confusion_matrix, f, indent=2)
