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

class Errors(object):

    def __init__(self):
        self.errors = {}
        self.errors['FP'] = {}
        self.errors['FN'] = {}
  
    def addError(self, instance_id, true_label, predicted_proba):
        if (true_label):
            self.errors['FN'][str(instance_id)] = predicted_proba
        else:
            self.errors['FP'][str(instance_id)] = predicted_proba

    def addFold(self, true_labels, instances_ids, predicted_proba):
        predicted_labels = [x > 0.5 for x in predicted_proba]
        for i in range(len(predicted_labels)):
            if predicted_labels[i] != true_labels[i]:
                self.addError(instances_ids[i], true_labels[i], predicted_proba[i])

    def toJson(self, f):
        json.dump(self.errors, f, indent = 2)
