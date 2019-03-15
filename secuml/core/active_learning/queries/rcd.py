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

import copy
import numpy as np
import os.path as path
import random
import time

from secuml.core.clustering.clusters import Clusters
from secuml.core.tools.core_exceptions import SecuMLcoreException

from .categories import Categories
from . import Queries


class RareCategoryAtLeastTwoFamilies(SecuMLcoreException):

    def __str__(self):
        return('Rare category detection requires that the initial annotated '
               'dataset contains at least two different families.')


class RcdQueries(Queries):

    def __init__(self, iteration, label, proba_min=None, proba_max=None,
                 input_checking=True):
        Queries.__init__(self, iteration, label=label)
        self.proba_min = proba_min
        self.proba_max = proba_max
        self.rcd_conf = self.iteration.conf.rcd_conf
        self.multiclass_model = None
        self._check_input_data(input_checking)

    def _check_input_data(self, input_checking):
        instances = self.iteration.datasets.instances
        self.annotated_instances = instances.get_annotated_instances(
                                                              label=self.label)
        annotations = self.annotated_instances.annotations
        families_counts = annotations.get_families_count()
        if len(families_counts) < 2:
            self.families_analysis = False
        else:
            families_counts = [(k, x) for k, x in families_counts.items()]
            families_counts.sort(key=lambda tup: tup[1], reverse=True)
            self.families_analysis = families_counts[1][1] >= 2
        if input_checking and not self.families_analysis:
            raise RareCategoryAtLeastTwoFamilies()

    def run(self, predictions, already_queried=None):
        Queries.run(self, predictions, already_queried=already_queried)
        self._gen_clustering_visu()

    def _set_predictions(self, predictions):
        if self.proba_min is not None and self.proba_max is not None:
            self.predictions = predictions.get_within_range(self.proba_min,
                                                            self.proba_max)
        else:
            self.predictions = predictions.to_list()

    def run_models(self):
        if self.families_analysis:
            self.annotations_type = 'families'
            start_time = time.time()
            self._build_categories()
            self.analysis_time = time.time() - start_time
            self.categories.set_likelihood()
        else:
            self.annotations_type = 'individual'
            self.categories = None
            self.analysis_time = 0

    def generate_queries(self, already_queried=None):
        num_annotations = self.rcd_conf.num_annotations
        if not self.families_analysis:
            indexes = range(len(self.predictions))
            if already_queried is not None:
                indexes = [i for i in indexes
                           if self.predictions[i].instance_id
                           not in already_queried]
            if len(indexes) > num_annotations:
                indexes = random.sample(indexes, num_annotations)
            for i in indexes:
                p = self.predictions[i]
                query = self.generate_query(p.instance_id, p.proba, self.label,
                                            None)
                self.add_query(query)
        else:
            self.categories.generate_queries(self.rcd_conf,
                                             already_queried=already_queried)

    def export(self):
        if not self.families_analysis:
            Queries.export(self)
        else:
            filename = path.join(self.iteration.iteration_dir,
                                 'toannotate_%s.json' % self.label)
            self.categories.export(filename)

    def annotate_auto(self):
        if not self.families_analysis:
            Queries.annotate_auto(self)
        else:
            self.categories.annotate_auto()

    def get_manual_annotations(self):
        if not self.families_analysis:
            Queries.get_manual_annotations(self)
        else:
            self.categories.get_manual_annotations()

    def _build_categories(self):
        train, test, test_predictions = self._build_multiclass_classifier()
        all_instances = copy.deepcopy(test)
        all_instances.union(train)
        if test.num_instances() > 0:
            predicted_families = test_predictions.values
            all_families = list(predicted_families)
            all_families.extend(train.annotations.get_families())
            predicted_proba = test_predictions.all_probas
            for family in train.annotations.get_families():
                probas = [int(family == s)
                          for s in self.multiclass_model.class_labels]
                predicted_proba = np.vstack((predicted_proba,
                                             np.array(probas)))
        else:
            all_families = self.annotated_instances.annotations.get_families()
            predicted_proba = None
            for family in all_families:
                probas = [int(family == s)
                          for s in self.multiclass_model.class_labels]
                if predicted_proba is None:
                    predicted_proba = np.array(probas)
                else:
                    predicted_proba = np.vstack((predicted_proba,
                                                 np.array(probas)))
        labels_values = list(self.multiclass_model.class_labels)
        assigned_categories = [labels_values.index(x) for x in all_families]
        self._set_categories(all_instances, assigned_categories,
                             predicted_proba)

    def _set_categories(self, all_instances, assigned_categories,
                        predicted_proba):
        self.categories = Categories(self.iteration,
                                     all_instances,
                                     assigned_categories,
                                     predicted_proba,
                                     self.label,
                                     self.multiclass_model.class_labels)

    def _get_multiclass_conf(self):
        return self.rcd_conf.classification_conf.classifier_conf

    def _build_multiclass_classifier(self):
        multiclass_conf = self._get_multiclass_conf().classifier_conf
        predicted_ids = [p.instance_id for p in self.predictions]
        instances = self.iteration.datasets.instances
        predicted_instances = instances.get_from_ids(predicted_ids)
        if self.multiclass_model is None:
            self.multiclass_model = multiclass_conf.model_class(
                                                               multiclass_conf)
            self.multiclass_model.training(self.annotated_instances)
            predictions, _ = self.multiclass_model.testing(predicted_instances)
        return self.annotated_instances, predicted_instances, predictions

    def _gen_clustering_visu(self):
        if self.families_analysis:
            clusters = Clusters(self.categories.instances,
                                self.categories.assigned_categories)
            clusters.generate(None, None)
