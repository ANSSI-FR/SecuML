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
import json
import numpy as np
import random

from secuml.core.classif.classifiers.gaussian_naive_bayes \
        import GaussianNaiveBayes
from .category import Category


class Categories(object):

    # assigned categories: array of int.
    #                      The index of the category associated to each
    #                      instance.
    # assignment_proba: array of float.
    #                   The probability associated to each instance.
    # category_labels: array of string.
    #                  The label of each category.
    def __init__(self, iteration, instances, assigned_categories,
                 assignment_proba, label, category_labels):
        self.iteration = iteration
        self.instances = instances
        self.generate(assigned_categories, assignment_proba, label,
                      category_labels)

    def init(self, label, families):
        self.categories = [Category(self.iteration, label, families[x])
                           for x in range(self.num_categories)]

    def num_categories(self):
        return self.num_categories

    def generate(self, assigned_categories, assignment_proba, label,
                 category_labels):
        self.assigned_categories = assigned_categories
        self.num_categories = len(set(assigned_categories))
        self.init(label, category_labels)
        for i, instance_id in enumerate(self.instances.ids.get_ids()):
            annotated = self.instances.annotations.is_annotated(instance_id)
            c = self.assigned_categories[i]
            probas = None
            if assignment_proba is not None:
                probas = assignment_proba[i, :]
            self.categories[c].add_instance(instance_id, probas, annotated)
        for c in range(self.num_categories):
            self.categories[c].final_computation()

    def export(self, filename):
        obj = {}
        for c in range(self.num_categories):
            obj[self.categories[c].family] = self.categories[c].export()
        with open(filename, 'w') as f:
            json.dump(obj, f, indent=2)

    def annotate_auto(self):
        for category in self.categories:
            category.annotate_auto()

    def get_manual_annotations(self):
        for category in self.categories:
            category.get_manual_annotations()

    def generate_queries(self, conf, already_queried=None):
        self.set_category_num_annotations(conf)
        for category in self.categories:
            category.generate_queries(conf.cluster_strategy,
                                      already_queried=already_queried)

    def set_category_num_annotations(self, conf):
        weights = np.full((self.num_categories,), 1 / self.num_categories)
        num_annotations = conf.num_annotations
        annotations = np.full((self.num_categories,), None)
        card = [self.categories[c].num_instances() -
                self.categories[c].num_annotated_instances
                for c in range(self.num_categories)]
        sum_card = sum(card)
        if num_annotations > sum_card:
            num_annotations = sum_card
            self.iteration.conf.logger.warning(
                'The number of instances is smaller than the requested number '
                'of annotation queries. '
                'The number of annotation queries is set to %d.' % (sum_card))
        num_remaining_annotations = num_annotations
        no_starve_cluster = False
        while not no_starve_cluster:
            no_starve_cluster = True
            weights = weights / np.sum(weights)
            for c in range(self.num_categories):
                if annotations[c] is not None:
                    continue
                num = int(weights[c] * num_remaining_annotations)
                if card[c] <= num:
                    annotations[c] = card[c]
                    weights[c] = 0
                    no_starve_cluster = False
            num_annotated = np.sum(annotations != None)  # NOQA: 711
            num_remaining_annotations = num_annotations - num_annotated
            if num_remaining_annotations == 0:
                break
        for c in range(self.num_categories):
            if annotations[c] is not None:
                continue
            num = int(weights[c] * num_remaining_annotations)
            annotations[c] = num
        num_remaining_annotations = num_annotations - sum(annotations)
        while num_remaining_annotations > 0:
            shuffled_clusters = list(range(self.num_categories))
            random.shuffle(shuffled_clusters)
            for c in shuffled_clusters:
                if num_remaining_annotations == 0:
                    break
                if card[c] > annotations[c]:
                    annotations[c] += 1
                    num_remaining_annotations -= 1
        for c, num in enumerate(annotations):
            self.categories[c].set_num_annotations(num)
        return annotations

    def set_likelihood(self):
        naive_bayes = self.train_naive_bayes()
        features = self.instances.features.get_values()
        for c in range(self.num_categories):
            mask = self.assigned_categories == c
            c_features = features[mask, :]
            c_likelihood = naive_bayes.log_likelihood(c_features, str(c))
            self.categories[c].set_likelihood(c_likelihood)

    def train_naive_bayes(self):
        naive_bayes_conf = self.get_naive_bayes_conf()
        families = self.instances.annotations.get_families()
        current_families = copy.deepcopy(families)
        # families are altered
        self.instances.annotations.set_families(self.assigned_categories)
        naive_bayes = GaussianNaiveBayes(naive_bayes_conf)
        naive_bayes.training(self.instances)
        # families are restored
        self.instances.annotations.set_families(current_families)
        return naive_bayes

    def get_naive_bayes_conf(self):
        return None
