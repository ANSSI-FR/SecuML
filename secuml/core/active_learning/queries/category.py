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

import pandas as pd
import scipy

from secuml.core.tools.matrix import sort_data_frame

from . import Queries


class Category(Queries):

    def __init__(self, iteration, label=None, family=None):
        Queries.__init__(self, iteration, label=label)
        self.assign_label_family(label, family)
        self.instances_ids = []
        self.probas = []
        self.entropy = []
        self.likelihood = []
        self.df = None

        self.num_annotations = None
        self.annotated_instances = []
        self.num_annotated_instances = 0

    def export(self):
        return {'instance_ids': self.get_ids(),
                'confidence': self.get_confidences(),
                'label': self.label}

    def assign_label_family(self, label, family):
        self.family = family
        if label != 'all':
            self.label = label
        else:
            self.label = label

    def num_instances(self):
        return len(self.instances_ids)

    def set_num_annotations(self, num_annotations):
        self.num_annotations = num_annotations

    def add_instance(self, instance_id, probas, annotated):
        self.instances_ids.append(instance_id)
        entropy = None
        proba = None
        likelihood = None
        if probas is not None:
            entropy = scipy.stats.entropy(probas)
            proba = max(probas)
        self.entropy.append(entropy)
        self.probas.append(proba)
        self.likelihood.append(likelihood)
        if annotated:
            self.annotated_instances.append(instance_id)
            self.num_annotated_instances += 1

    def final_computation(self):
        self.df = pd.DataFrame({'proba': self.probas,
                                'entropy': self.entropy,
                                'likelihood': self.likelihood},
                               index=list(map(str, self.instances_ids)))

    def set_likelihood(self, likelihood):
        self.likelihood = likelihood
        self.df['likelihood'] = likelihood

    def get_likelihood(self, instances):
        df = pd.DataFrame({'likelihood': self.likelihood},
                          index=list(map(str, self.instances_ids)))
        selected_df = df.loc[list(map(str, instances)), :]
        return selected_df['likelihood'].tolist()

    @staticmethod
    def from_json(obj):
        category = Category()
        category.instances_ids = obj['instances_ids']
        category.label = obj['label']
        return category

    def generate_queries(self, cluster_strategy, already_queried=None):
        queries_types = cluster_strategy.split('_')
        num_queries_types = len(queries_types)
        if already_queried is None:
            already_queried = []
        for q, queries_type in enumerate(queries_types):
            drop_instances = already_queried[:]
            drop_instances.extend(self.annotated_instances)
            if q == (num_queries_types - 1):
                num_queries = self.num_annotations - len(self.annotation_queries)
            else:
                num_queries = self.num_annotations // num_queries_types
            if num_queries == 0:
                continue
            queries_df = self._get_selected_instances(drop_instances)
            if queries_type == 'center':
                confidence = 'high'
                sort_data_frame(queries_df, 'likelihood', False, True)
                queries_df = queries_df.head(num_queries)
            elif queries_type == 'anomalous':
                confidence = 'low'
                sort_data_frame(queries_df, 'likelihood', True, True)
                queries_df = queries_df.head(num_queries)
            elif queries_type == 'uncertain':
                confidence = 'low'
                sort_data_frame(queries_df, 'entropy', False, True)
                queries_df = queries_df.head(num_queries)
            elif queries_type == 'random':
                confidence = 'low'
                queries_df = queries_df.sample(n=num_queries, axis=0)
            else:
                raise ValueError()
            self._add_queries(confidence, queries_df)

    def _add_queries(self, confidence, queries_df):
        for index, row in queries_df.iterrows():
            query = self.generate_query(int(index), row['likelihood'],
                                        self.label, self.family,
                                        confidence=confidence)
            self.add_query(query)
            self.annotated_instances.append(int(index))

    def _get_selected_instances(self, drop_instances):
        selected_instances = self.instances_ids
        if drop_instances is not None:
            selected_instances = [
                x for x in selected_instances if x not in drop_instances]
        return self.df.loc[list(map(str, selected_instances)), :]
