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

import json
import numpy as np
import os.path as path
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

    def display_matrix(self, f):
        json.dump({'TP': self.get_true_positives(),
                   'TN': self.get_true_negatives(),
                   'FP': self.get_false_positives(),
                   'FN': self.get_false_negatives()},
                  f, indent=2)

    def display(self, directory):
        with open(path.join(directory, 'confusion_matrix.json'), 'w') as f:
            self.display_matrix(f)
