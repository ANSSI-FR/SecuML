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

import json

class BinaryErrors(object):

    def __init__(self, conf):
        self.errors = {}
        self.errors['FP'] = {}
        self.errors['FN'] = {}
        self.probabilist_model = conf.probabilistModel()

    def addFold(self, true_labels, instances_ids, predicted_labels, predicted_proba, predicted_scores):
        scores = predicted_proba if self.probabilist_model else predicted_scores
        for i in range(len(predicted_labels)):
            if predicted_labels[i] != true_labels[i]:
                self.addError(instances_ids[i], true_labels[i], scores[i])

    def addError(self, instance_id, true_label, score):
        if (true_label):
            self.errors['FN'][str(instance_id)] = score
        else:
            self.errors['FP'][str(instance_id)] = score

    def toJson(self, f):
        json.dump(self.errors, f, indent = 2)
