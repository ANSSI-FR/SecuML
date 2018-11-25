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

import copy
import numpy as np
import os.path as path
import random
import time

from SecuML.core.classification.ClassifierDatasets import ClassifierDatasets
from SecuML.core.clustering.Clustering import Clustering

from SecuML.core.tools import matrix_tools
from SecuML.core.tools.core_exceptions import SecuMLcoreException

from .Queries import Queries

from .Categories import Categories


class RareCategoryAtLeastTwoFamilies(SecuMLcoreException):

    def __str__(self):
        return('Rare category detection requires that the initial annotated '
               'dataset contains at least two different families.')


class RareCategoryDetectionQueries(Queries):

    def __init__(self, iteration, label, proba_min, proba_max,
                 input_checking=True):
        Queries.__init__(self, iteration, label=label)
        self.proba_min = proba_min
        self.proba_max = proba_max
        self.rcd_conf = self.iteration.conf.rcd_conf
        self.multiclass_model = None
        if input_checking:
            self.checkInputData()

    def checkInputData(self):
        train_instances = self.iteration.datasets.instances.getAnnotatedInstances()
        num_families = len(train_instances.annotations.getFamiliesValues())
        if num_families < 2:
            raise RareCategoryAtLeastTwoFamilies()

    def run(self, already_queried=None):
        self.predictions = self.getPredictedProbabilities()
        self.runModels(already_queried=already_queried)
        start_time = time.time()
        self.generateQueries()
        self.generate_queries_time = time.time() - start_time
        self.exportAnnotationQueries()
        self.generateClusteringVisualization()

    def runModels(self, already_queried=None):
        df = matrix_tools.extract_rows_with_thresholds(self.predictions,
                                                    self.proba_min,
                                                    self.proba_max,
                                                    'predicted_proba')
        if already_queried is not None:
            self.predicted_ids = list(
                set(df.index).difference(set(already_queried)))
        else:
            self.predicted_ids = list(df.index)
        datasets = self.iteration.datasets
        self.annotated_instances = datasets.instances.getAnnotatedInstances(
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

    def generateQueries(self):
        num_annotations = self.rcd_conf.num_annotations
        if not self.families_analysis:
            selected_instances = self.predicted_ids
            if len(selected_instances) > num_annotations:
                selected_instances = random.sample(
                    selected_instances, num_annotations)
            self.annotation_queries = []
            for instance_id in selected_instances:
                predicted_proba = self.predictions.loc[instance_id]['predicted_proba']
                query = self.generateQuery(
                    instance_id, predicted_proba, self.label, None)
                self.annotation_queries.append(query)
        else:
            self.categories.generateQueries(self.rcd_conf)

    def exportAnnotationQueries(self):
        if not self.families_analysis:
            Queries.exportAnnotationQueries(self)
        else:
            filename = path.join(self.iteration.iteration_dir,
                                 'toannotate_%s.json' % self.label)
            self.categories.exportAnnotationQueries(filename)

    def annotateAuto(self):
        if not self.families_analysis:
            Queries.annotateAuto(self)
        else:
            self.categories.annotateAuto(self.iteration)

    def getManualAnnotations(self):
        if not self.families_analysis:
            Queries.getManualAnnotations(self)
        else:
            self.categories.getManualAnnotations(self.iteration)

    def buildCategories(self):
        train, test = self.buildMulticlassClassifier()
        all_instances = copy.deepcopy(test)
        all_instances.union(train)
        if test.numInstances() > 0:
            predicted_families = self.multiclass_model.testing_monitoring.getPredictedLabels()
            all_families = list(predicted_families)
            all_families.extend(train.annotations.getFamilies())
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
        return self.rcd_conf.classification_conf.classifier_conf

    def buildMulticlassClassifier(self):
        multiclass_conf = self.getMulticlassConf().classifier_conf
        datasets = self.iteration.datasets
        predicted_instances = datasets.instances.getInstancesFromIds(self.predicted_ids)
        multiclass_datasets = ClassifierDatasets(None,
                                                 multiclass_conf.sample_weight)
        multiclass_datasets.setDatasets(self.annotated_instances,
                                        predicted_instances, None)
        if self.multiclass_model is None:
            self.multiclass_model = multiclass_conf.model_class(multiclass_conf)
            self.multiclass_model.training(multiclass_datasets)
            self.multiclass_model.crossValidationMonitoring(multiclass_datasets)
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
        return families_counts[1][1] >= 2

    def generateClusteringVisualization(self):
        if self.families_analysis:
            clustering = Clustering(self.categories.instances,
                                    self.categories.assigned_categories)
            clustering.generateClustering(None, None)
