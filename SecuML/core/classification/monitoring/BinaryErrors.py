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
        for kind in ['FP', 'FN']:
            self.errors[kind] = {'ids': [], 'scores': []}
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
        kind = 'FN' if ground_truth else 'FP'
        self.errors[kind]['ids'].append(instance_id)
        self.errors[kind]['scores'].append(score)

    def to_json(self, f):
        json.dump(self.errors, f, indent=2)
