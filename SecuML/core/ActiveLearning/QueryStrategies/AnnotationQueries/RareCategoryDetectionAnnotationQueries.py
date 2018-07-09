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
import numpy as np
import os.path as path
import random
import time

from SecuML.core.Classification.ClassifierDatasets import ClassifierDatasets
from SecuML.core.Clustering.Clustering import Clustering

from SecuML.core.Tools import matrix_tools

from .AnnotationQueries import AnnotationQueries

from .Categories import Categories


class RareCategoryAtLeastTwoFamilies(Exception):

    def __str__(self):
        return '''Rare category detection requires that the initial annotated dataset
                  contains at least two different families.'''


class RareCategoryDetectionAnnotationQueries(AnnotationQueries):

    def __init__(self, iteration, label, proba_min, proba_max, input_checking=True):
        AnnotationQueries.__init__(self, iteration, label)
        self.proba_min = proba_min
        self.proba_max = proba_max
        self.rare_category_detection_conf = self.iteration.conf.rare_category_detection_conf
        self.multiclass_model = None
        if input_checking:
            self.checkInputData()

    def checkInputData(self):
        train_instances = self.iteration.datasets.getAnnotatedInstances()
        num_families = len(train_instances.annotations.getFamiliesValues())
        if num_families < 2:
            raise RareCategoryAtLeastTwoFamilies()

    def run(self, already_queried=None):
        self.predictions = self.getPredictedProbabilities()
        self.runModels(already_queried=already_queried)
        start_time = time.time()
        self.generateAnnotationQueries()
        self.generate_queries_time = time.time() - start_time
        self.exportAnnotationQueries()
        self.generateClusteringVisualization()

    def runModels(self, already_queried=None):
        df = matrix_tools.extractRowsWithThresholds(self.predictions,
                                                    self.proba_min, self.proba_max, 'predicted_proba')
        if already_queried is not None:
            self.predicted_ids = list(
                set(df.index).difference(set(already_queried)))
        else:
            self.predicted_ids = list(df.index)
        datasets = self.iteration.datasets
        self.annotated_instances = datasets.getAnnotatedInstances(
            label=self.label)
        self.families_analysis = self.familiesAnalysis()
        if self.families_analysis:
            self.annotations_type = 'families'
            start_time = time.time()
            self.buildCategories()
            self.analysis_time = time.time() - start_time
            self.categories.setLikelihood()
        else:
            self.annotations_type = 'individual'
            self.categories = None
            self.analysis_time = 0

    def generateAnnotationQueries(self):
        num_annotations = self.rare_category_detection_conf.num_annotations
        if not self.families_analysis:
            selected_instances = self.predicted_ids
            if len(selected_instances) > num_annotations:
                selected_instances = random.sample(
                    selected_instances, num_annotations)
            self.annotation_queries = []
            for instance_id in selected_instances:
                predicted_proba = self.predictions.loc[instance_id]['predicted_proba']
                query = self.generateAnnotationQuery(
                    instance_id, predicted_proba, self.label, None)
                self.annotation_queries.append(query)
        else:
            self.categories.generateAnnotationQueries(
                self.rare_category_detection_conf)

    def exportAnnotationQueries(self):
        if not self.families_analysis:
            AnnotationQueries.exportAnnotationQueries(self)
        else:
            filename = path.join(self.iteration.iteration_dir,
                                 'toannotate_' + self.label + '.json')
            self.categories.exportAnnotationQueries(filename)

    def annotateAuto(self):
        if not self.families_analysis:
            AnnotationQueries.annotateAuto(self)
        else:
            self.categories.annotateAuto(self.iteration)

    def getManualAnnotations(self):
        if not self.families_analysis:
            AnnotationQueries.getManualAnnotations(self)
        else:
            self.categories.getManualAnnotations(self.iteration)

    def checkAnnotationQueriesAnswered(self):
        if not self.families_analysis:
            return AnnotationQueries.checkAnnotationQueriesAnswered(self)
        else:
            return self.categories.checkAnnotationQueriesAnswered(self.iteration)

    def buildCategories(self):
        train, test = self.buildMulticlassClassifier()
        all_instances = copy.deepcopy(test)
        all_instances.union(train)
        if test.numInstances() > 0:
            predicted_families = self.multiclass_model.testing_monitoring.getPredictedLabels()
            all_families = list(predicted_families) + \
                train.annotations.getFamilies()
            predicted_proba = self.multiclass_model.testing_monitoring.getAllPredictedProba()
            for family in train.annotations.getFamilies():
                probas = [int(family == s)
                          for s in self.multiclass_model.class_labels]
                predicted_proba = np.vstack(
                    (predicted_proba, np.array(probas)))
        else:
            all_families = self.annotated_instances.annotations.getFamilies()
            predicted_proba = None
            for family in all_families:
                probas = [int(family == s)
                          for s in self.multiclass_model.class_labels]
                if predicted_proba is None:
                    predicted_proba = np.array(probas)
                else:
                    predicted_proba = np.vstack(
                        (predicted_proba, np.array(probas)))
        labels_values = list(self.multiclass_model.class_labels)
        assigned_categories = [labels_values.index(x) for x in all_families]
        self.setCategories(all_instances, assigned_categories, predicted_proba)

    def setCategories(self, all_instances, assigned_categories, predicted_proba):
        self.categories = Categories(self.iteration,
                                     all_instances,
                                     assigned_categories,
                                     predicted_proba,
                                     self.label,
                                     self.multiclass_model.class_labels)

    def getMulticlassConf(self):
        multiclass_conf = self.rare_category_detection_conf.classification_conf
        return multiclass_conf

    def buildMulticlassClassifier(self):
        multiclass_conf = self.getMulticlassConf()
        datasets = self.iteration.datasets
        predicted_instances = datasets.getInstancesFromIds(self.predicted_ids)
        multiclass_datasets = ClassifierDatasets(None,
                                                 multiclass_conf.sample_weight)
        multiclass_datasets.setDatasets(self.annotated_instances,
                                        predicted_instances)
        if self.multiclass_model is None:
            self.multiclass_model = multiclass_conf.model_class(
                multiclass_conf, cv_monitoring=True)
            self.multiclass_model.training(multiclass_datasets)
            self.multiclass_model.testing(multiclass_datasets)
            if multiclass_datasets.validation_instances is not None:
                self.multiclass_model.validation(multiclass_datasets)
        return multiclass_datasets.train_instances, multiclass_datasets.test_instances

    # A multi class supervised model is learned from the annotated instances if:
    #       - there are at most two families
    #       - the second most represented family has at least two instances
    def familiesAnalysis(self):
        num_families = len(
            self.annotated_instances.annotations.getFamiliesValues())
        if num_families < 2:
            return False
        families_counts = self.annotated_instances.annotations.getFamiliesCount()
        families_counts = [(k, x) for k, x in families_counts.items()]
        families_counts.sort(key=lambda tup: tup[1], reverse=True)
        if families_counts[1][1] < 2:
            return False
        return True

    def generateClusteringVisualization(self):
        if self.families_analysis:
            clustering = Clustering(self.categories.instances,
                                    self.categories.assigned_categories)
            clustering.generateClustering(None, None)
        else:
            self.clustering_exp = None
