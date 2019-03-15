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

import abc
import csv
import os.path as path
import time

from secuml.core.tools.core_exceptions import SecuMLcoreException


class Queries(object):

    def __init__(self, iteration, label=None):
        self.iteration = iteration
        self.label = label
        self.annotation_queries = []

    def run(self, predictions, already_queried=None):
        self._set_predictions(predictions)
        self.run_models()
        start_time = time.time()
        self.generate_queries(already_queried=already_queried)
        self.exec_time = time.time() - start_time
        self.export()

    def get_ids(self):
        return [q.instance_id for q in self.annotation_queries]

    def get_confidences(self):
        return [q.confidence for q in self.annotation_queries]

    @abc.abstractmethod
    def run_models(self):
        return

    @abc.abstractmethod
    def generate_queries(self, already_queried=None):
        return

    def _set_predictions(self, predictions):
        self.predictions = predictions

    def add_query(self, query):
        self.annotation_queries.append(query)

    def export(self):
        iteration_dir = self.iteration.iteration_dir
        if iteration_dir is None:
            return
        if self.label is None:
            filename = 'toannotate.csv'
        else:
            filename = 'toannotate_%s.csv' % self.label
        filename = path.join(iteration_dir, filename)
        with open(filename, 'w') as f:
            for i, annotation_query in enumerate(self.annotation_queries):
                if i == 0:
                    annotation_query.display_header(f)
                annotation_query.export(f)

    def annotate_auto(self):
        for annotation_query in self.annotation_queries:
            annotation_query.annotate_auto(self.iteration, self.label)

    def get_manual_annotations(self):
        for annotation_query in self.annotation_queries:
            annotation_query.get_manual_annotation(self.iteration)

    def get_instance_ids(self):
        return [annotation_query.instance_id
                for annotation_query in self.annotation_queries]


class NoAnnotationBudget(SecuMLcoreException):
    def __str__(self):
        return 'The annotation budget has run out'


class Query(object):

    def __init__(self, instance_id, predicted_proba, suggested_label,
                 suggested_family, confidence=None):
        self.instance_id = instance_id
        self.predicted_proba = predicted_proba
        self.suggested_label = suggested_label
        self.suggested_family = suggested_family
        self.confidence = confidence

    def display_header(self, f):
        csv_writer = csv.writer(f)
        csv_writer.writerow(['instance_id', 'predicted_proba',
                             'suggested_label', 'suggested_family',
                             'confidence'])

    def export(self, f):
        csv_writer = csv.writer(f)
        csv_writer.writerow([self.instance_id, self.predicted_proba,
                             self.suggested_label, self.suggested_family,
                             self.confidence])

    def to_json(self):
        return {'instance_id': self.instance_id,
                'predicted_proba': self.predicted_proba,
                'suggested_label': self.suggested_label,
                'suggested_family': self.suggested_family,
                'confidence': self.confidence}

    def update_datasets(self, iteration, label, family):
        if iteration.budget <= 0:
            raise NoAnnotationBudget()
        iteration.budget -= 1
        iteration.datasets.update(self.instance_id, label, family)
        iteration.suggestions_accuracy.add_annotation(self.suggested_label,
                                                      self.suggested_family,
                                                      label, family,
                                                      self.confidence)
