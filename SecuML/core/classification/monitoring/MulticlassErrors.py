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


class MulticlassErrors(object):

    def __init__(self):
        self.errors = []

    def addFold(self, predictions):
        for i in range(predictions.numInstances()):
            if predictions.ground_truth[i] != predictions.predictions[i]:
                self.errors.append(predictions.ids.ids[i])

    def to_json(self, f):
        json.dump({'errors': self.errors}, f, indent=2)
