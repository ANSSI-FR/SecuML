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

import csv

from SecuML.core.tools.core_exceptions import SecuMLcoreException


class NoAnnotationBudget(SecuMLcoreException):
    def __str__(self):
        return 'The annotation budget has run out'


class Query(object):

    def __init__(self, instance_id, predicted_proba,
                 suggested_label, suggested_family,
                 confidence=None):
        self.instance_id = instance_id
        self.predicted_proba = predicted_proba
        self.suggested_label = suggested_label
        self.suggested_family = suggested_family
        self.confidence = confidence

    def displayHeader(self, f):
        header = ['instance_id', 'predicted_proba',
                  'suggested_label', 'suggested_family',
                  'confidence']
        csv_writer = csv.writer(f)
        csv_writer.writerow(header)

    def export(self, f):
        line = [self.instance_id, self.predicted_proba, self.suggested_label,
                self.suggested_family, self.confidence]
        csv_writer = csv.writer(f)
        csv_writer.writerow(line)

    def to_json(self):
        obj = {}
        obj['instance_id'] = self.instance_id
        obj['predicted_proba'] = self.predicted_proba
        obj['suggested_label'] = self.suggested_label
        obj['suggested_family'] = self.suggested_family
        obj['confidence'] = self.confidence
        return obj

    def updateDatasets(self, iteration, label, family):
        if iteration.budget <= 0:
            raise NoAnnotationBudget()
        iteration.budget -= 1
        iteration.datasets.update(self.instance_id, label, family)
        iteration.monitoring.suggestions.addAnnotation(self.suggested_label,
                                                       self.suggested_family,
                                                       label, family,
                                                       self.confidence)
