# SecuML
# Copyright (C) 2016-2017  ANSSI
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
import pandas as pd
import scipy

from SecuML.core.Tools import matrix_tools

from .AnnotationQuery import AnnotationQuery


class Category(object):

    def __init__(self, label=None, family=None):
        self.assignLabelFamily(label, family)
        self.instances_ids = []
        self.probas = []
        self.entropy = []
        self.likelihood = []
        self.df = None
        self.annotation_queries = {}

        self.annotated_instances = []
        self.num_annotated_instances = 0

        # To display the annotation queries in the web GUI
        self.queries = []
        self.queries_confidence = []

    def generateAnnotationQuery(self, instance_id, predicted_proba,
                                suggested_label, suggested_family, confidence=None):
        return AnnotationQuery(instance_id, predicted_proba,
                               suggested_label, suggested_family, confidence=confidence)

    def assignLabelFamily(self, label, family):
        self.family = family
        if label != 'all':
            self.label = label
        else:
            self.label = label

    def numInstances(self):
        return len(self.instances_ids)

    def setWeight(self, weight):
        self.weight = weight

    def setNumAnnotations(self, num_annotations):
        self.num_annotations = num_annotations

    def addInstance(self, instance_id, probas, annotated):
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

    def finalComputation(self):
        self.df = pd.DataFrame({'proba': self.probas,
                                'entropy': self.entropy,
                                'likelihood': self.likelihood},
                               index=list(map(str, self.instances_ids)))

    def annotateAuto(self, iteration):
        for k, queries in self.annotation_queries.items():
            for q, query in enumerate(queries):
                query.annotateAuto(iteration, self.label)

    def getManualAnnotations(self, iteration):
        for k, queries in self.annotation_queries.items():
            for q, query in enumerate(queries):
                query.getManualAnnotation(iteration)

    def checkAnnotationQueriesAnswered(self, iteration):
        for k, queries in self.annotation_queries.items():
            for q, query in enumerate(queries):
                if not query.checkAnswered(iteration):
                    return False
        return True

    def setLikelihood(self, likelihood):
        self.likelihood = likelihood
        self.df['likelihood'] = likelihood

    def getLikelihood(self, instances):
        df = pd.DataFrame({'likelihood': self.likelihood},
                          index=list(map(str, self.instances_ids)))
        selected_df = df.loc[list(map(str, instances)), :]
        return selected_df['likelihood'].tolist()

    def getCategoryLabel(self):
        return self.label

    def getCategoryFamily(self):
        return self.family

    def toJson(self):
        obj = {}
        obj['label'] = self.label
        obj['family'] = self.family
        obj['annotation_queries'] = {}
        for kind, queries in self.annotation_queries.items():
            obj['annotation_queries'][kind] = []
            for q, query in enumerate(queries):
                obj['annotation_queries'][kind].append(query.toJson())
        return obj

    @staticmethod
    def fromJson(obj):
        category = Category()
        category.instances_ids = obj['instances_ids']
        category.label = obj['label']
        return category

    def exportAnnotationQueries(self):
        annotation_queries = {}
        annotation_queries['instance_ids'] = self.queries
        annotation_queries['confidence'] = self.queries_confidence
        annotation_queries['label'] = self.label
        return annotation_queries

    def generateAnnotationQueries(self, cluster_strategy):
        queries_types = cluster_strategy.split('_')
        num_queries_types = len(queries_types)
        total_num_queries = 0
        annotated_instances = copy.deepcopy(self.annotated_instances)
        for q, queries_type in enumerate(queries_types):
            if q == (num_queries_types - 1):
                num_queries = self.num_annotations - total_num_queries
            else:
                num_queries = self.num_annotations // num_queries_types
            if queries_type == 'center':
                queries = self.queryHighLikelihoodInstances(
                    annotated_instances, num_queries)
            elif queries_type == 'anomalous':
                queries = self.queryLowLikelihoodInstances(
                    annotated_instances, num_queries)
            elif queries_type == 'uncertain':
                queries = self.queryUncertainInstances(
                    annotated_instances, num_queries)
            elif queries_type == 'random':
                queries = self.queryRandomInstances(
                    annotated_instances, num_queries)
            else:
                raise ValueError()
            annotated_instances += queries
            total_num_queries += len(queries)
        assert(total_num_queries == self.num_annotations)

    def queryUncertainInstances(self, drop_instances, num_instances):
        if num_instances == 0:
            return []
        queries_df = self.getSelectedInstancesDataframe(drop_instances)
        matrix_tools.sortDataFrame(queries_df, 'entropy', False, True)
        queries_df = queries_df.head(num_instances)
        self.addAnnotationQueries('uncertain', 'low', queries_df)
        return list(map(int, queries_df.index.values.tolist()))

    def queryHighLikelihoodInstances(self, drop_instances, num_instances):
        if num_instances == 0:
            return []
        queries_df = self.getSelectedInstancesDataframe(drop_instances)
        matrix_tools.sortDataFrame(queries_df, 'likelihood', False, True)
        queries_df = queries_df.head(num_instances)
        self.addAnnotationQueries('high_likelihood', 'high', queries_df)
        return list(map(int, queries_df.index.values.tolist()))

    def queryLowLikelihoodInstances(self, drop_instances, num_instances):
        if num_instances == 0:
            return []
        queries_df = self.getSelectedInstancesDataframe(drop_instances)
        matrix_tools.sortDataFrame(queries_df, 'likelihood', True, True)
        queries_df = queries_df.head(num_instances)
        self.addAnnotationQueries('low_likelihood', 'low', queries_df)
        return list(map(int, queries_df.index.values.tolist()))

    def queryRandomInstances(self, drop_instances, num_instances):
        if num_instances == 0:
            return []
        queries_df = self.getSelectedInstancesDataframe(drop_instances)
        queries_df = queries_df.sample(n=num_instances, axis=0)
        self.addAnnotationQueries('random', 'low', queries_df)
        return list(map(int, queries_df.index.values.tolist()))

    def addAnnotationQueries(self, kind, confidence, queries_df):
        if kind not in list(self.annotation_queries.keys()):
            self.annotation_queries[kind] = []
        for index, row in queries_df.iterrows():
            query = self.generateAnnotationQuery(int(index), row['likelihood'],
                                                 self.label, self.family, confidence=confidence)
            self.annotation_queries[kind].append(query)
            self.queries.append(int(index))
            self.queries_confidence.append(confidence)

    def getSelectedInstancesDataframe(self, drop_instances):
        if drop_instances is None:
            selected_instances = self.instances_ids
        else:
            selected_instances = [
                x for x in self.instances_ids if x not in drop_instances]
        selected_df = self.df.loc[list(map(str, selected_instances)), :]
        return selected_df
