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

class MulticlassErrors(object):

    def __init__(self):
        self.errors = []

    def addFold(self, true_labels, instances_ids, predicted_labels):
        for i in range(len(predicted_labels)):
            if true_labels[i] != predicted_labels[i]:
                self.errors.append(instances_ids[i])

    def toJson(self, f):
        json.dump({'errors': self.errors}, f, indent = 2)
