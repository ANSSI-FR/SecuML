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


class BinaryErrors(object):

    def __init__(self, conf):
        self.errors = {}
        self.errors['FP'] = {}
        self.errors['FN'] = {}
        self.probabilist_model = conf.probabilistModel()

    def addFold(self, predictions):
        if self.probabilist_model:
            scores = predictions.predicted_proba
        else:
            scores = predictions.predicted_scores
        for i in range(predictions.numInstances()):
            if predictions.predictions[i] != predictions.ground_truth[i]:
                self.addError(predictions.ids.ids[i],
                              predictions.ground_truth[i],
                              scores[i])

    def addError(self, instance_id, ground_truth, score):
        if (ground_truth):
            self.errors['FN'][str(instance_id)] = score
        else:
            self.errors['FP'][str(instance_id)] = score

    def toJson(self, f):
        json.dump(self.errors, f, indent=2)
