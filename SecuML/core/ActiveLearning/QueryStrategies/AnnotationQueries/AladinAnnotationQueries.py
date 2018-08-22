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
import pandas as pd
import time

from SecuML.core.Classification.Configuration.GaussianNaiveBayesConfiguration import GaussianNaiveBayesConfiguration
from SecuML.core.Classification.Configuration.TestConfiguration.UnlabeledLabeledConf import UnlabeledLabeledConf
from SecuML.core.Classification.Classifiers.GaussianNaiveBayes import GaussianNaiveBayes
from SecuML.core.Classification.ClassifierDatasets import ClassifierDatasets

from SecuML.core.Clustering.Evaluation.PerformanceIndicators import PerformanceIndicators

from SecuML.core.Tools import matrix_tools

from .AnnotationQueries import AnnotationQueries


class AladinAtLeastTwoFamilies(Exception):

    def __str__(self):
        return '''Aladin requires that the initial annotated dataset
                  contains at least two different families.'''


class AladinAnnotationQueries(AnnotationQueries):

    def __init__(self, iteration, conf):
        AnnotationQueries.__init__(self, iteration, 'aladin')
        self.num_annotations = conf.num_annotations
        self.conf = conf
        self.checkInputData()

    def runModels(self):
        self.datasets = self.iteration.update_model.datasets
        self.getLogisticRegressionResults()
        self.runNaiveBayes()

    def generateAnnotationQueries(self):
        self.computeScores()
        self.generateQueriesFromScores()

    def checkInputData(self):
        train_instances = self.iteration.datasets.getAnnotatedInstances()
        num_families = len(set(train_instances.annotations.getFamilies()))
        if num_families < 2:
            raise AladinAtLeastTwoFamilies()

    def getLogisticRegressionResults(self):
        multiclass = self.iteration.update_model.models['multiclass']
        self.lr_predicted_proba = multiclass.testing_monitoring.predictions_monitoring.all_predicted_proba
        self.lr_predicted_labels = multiclass.testing_monitoring.predictions_monitoring.predictions[
            'predictions']
        self.lr_class_labels = multiclass.class_labels
        self.lr_time = multiclass.training_execution_time
        self.lr_time += multiclass.testing_execution_time

    def createNaiveBayesConf(self):
        test_conf = UnlabeledLabeledConf()
        naive_bayes_conf = GaussianNaiveBayesConfiguration(
            4, False, True, test_conf)
        return naive_bayes_conf

    def runNaiveBayes(self):
        naive_bayes_conf = self.createNaiveBayesConf()
        # Update training data - the naive Bayes classifier is trained on all the data
        self.datasets.test_instances.annotations.setFamilies(
            list(self.lr_predicted_labels))
        all_datasets = ClassifierDatasets(None, naive_bayes_conf.sample_weight)
        train_instances = copy.deepcopy(self.datasets.train_instances)
        train_instances.union(self.datasets.test_instances)
        all_datasets.setDatasets(train_instances, None)
        self.evalClusteringPerf(all_datasets.train_instances)
        # Train the naive Bayes detection model and predict
        self.naive_bayes = GaussianNaiveBayes(naive_bayes_conf)
        self.naive_bayes.training(all_datasets)
        self.nb_time = self.naive_bayes.training_execution_time
        num_test_instances = self.datasets.test_instances.numInstances()
        self.datasets.test_instances.annotations.setFamilies(
            [None] * num_test_instances)
        if num_test_instances == 0:
            self.nb_predicted_log_proba = []
        else:
            self.nb_predicted_log_proba = self.naive_bayes.pipeline.predict_log_proba(
                self.datasets.test_instances.features.getValues())
        start_time = time.time()
        if num_test_instances == 0:
            self.nb_predicted_labels = []
        else:
            self.nb_predicted_labels = self.naive_bayes.pipeline.predict(
                self.datasets.test_instances.features.getValues())
        self.nb_time += time.time() - start_time
        self.nb_class_labels = self.naive_bayes.class_labels

    def evalClusteringPerf(self, instances):
        self.clustering_perf = PerformanceIndicators()
        self.clustering_perf.generateEvaluation(
            instances.ground_truth.getFamilies(), instances.annotations.getFamilies())

    def computeScores(self):
        self.createScoresDataFrame()
        self.computeUncertaintyScores()
        self.computeAnomalousScores()

    def createScoresDataFrame(self):
        test_instances = self.datasets.test_instances
        num_test_instances = self.datasets.test_instances.numInstances()
        self.scores = pd.DataFrame(np.zeros((num_test_instances, 5)),
                                   index=test_instances.ids.getIds(),
                                   columns=['lr_prediction', 'lr_score', 'nb_prediction', 'nb_score', 'queried'])
        self.scores['queried'] = [False] * num_test_instances

    # Uncertain instances have a low difference between the probability of belonging to
    # the most likely family and the second most likely family.
    # In Aladin, the authors consider this measure of uncertainty instead of the entropy
    # used by Pelleg and Moore (Active Learning for Anomaly and Rare-Category Detection).
    def computeUncertaintyScores(self):
        self.scores['lr_prediction'] = self.lr_predicted_labels
        lr_scores = []
        for i, predicted_label in enumerate(self.scores['lr_prediction']):
            predicted_label_index = np.where(
                self.lr_class_labels == predicted_label)[0]
            predicted_proba = self.lr_predicted_proba[i, predicted_label_index]
            proba = predicted_proba - self.lr_predicted_proba[i, :]
            proba[predicted_label_index] = 2
            score = np.min(proba)
            lr_scores.append(score)
        self.scores['lr_score'] = lr_scores

    # Anomalous instances have a low probability of belonging to the assigned family
    def computeAnomalousScores(self):
        self.scores['nb_prediction'] = self.nb_predicted_labels
        for c in set(self.nb_predicted_labels):
            c_instances = self.scores.loc[self.scores['nb_prediction']
                                          == c].index.values
            c_features = self.datasets.test_instances.features.getInstancesFromIds(
                c_instances)
            c_likelihood = self.naive_bayes.logLikelihood(c_features, c)
            self.scores.loc[self.scores['nb_prediction']
                            == c, 'nb_score'] = c_likelihood

    def generateQueriesFromScores(self):
        assert(np.array_equal(self.lr_class_labels, self.nb_class_labels))
        lr_predicted_proba_df = self.generateLrPredictedProbaDataFrame()
        num_families = len(self.lr_class_labels)
        self.annotation_queries = []

        # There are fewer annotation queries than the number of families
        if self.num_annotations <= num_families:
            if self.iteration.iteration_number % 2 == 0:
                classifier = 'lr'
            else:
                classifier = 'nb'
            matrix_tools.sortDataFrame(
                self.scores, classifier + '_score', True, True)
            selected_instances = self.scores.index.tolist()[
                :self.num_annotations]
            for instance_id in selected_instances:
                query = self.generateAnnotationQuery(
                    instance_id, 0, None, None)
                self.annotation_queries.append(query)
            return

        # Otherwise
        num_uncertain = [0] * num_families
        num_anomalous = [0] * num_families
        families_scores = self.generateFamiliesScoresTables()
        num_annotations = 0
        stop = False
        selected_instances = []
        while not stop:
            for i, family in enumerate(list(self.lr_class_labels)):
                if num_uncertain[i] <= num_anomalous[i]:
                    classifier = 'lr'
                    num_uncertain[i] += 1
                else:
                    classifier = 'nb'
                    num_anomalous[i] += 1
                scores = families_scores[classifier][i]
                selected_rows = scores.loc[scores['queried'] == False]
                if len(selected_rows) > 0:
                    query = selected_rows.index.tolist()[0]
                else:
                    # No anomalous or uncertain instances available for annotation
                    # Select the most likely instance according to the logistic regression output
                    self.conf.logger.debug(
                        family + ': no anomalous, no uncertain instances')
                    selected_rows = lr_predicted_proba_df.loc[lr_predicted_proba_df['queried'] == False]
                    selected_rows = matrix_tools.sortDataFrame(
                        selected_rows, family, False, False)
                    selection = selected_rows.index.tolist()
                    # Break condition - There is no instance left in the unlabelled pool
                    if len(selection) == 0:
                        stop = True
                        break
                    else:
                        query = selection[0]
                # Add annotation query and set queried = True
                num_annotations += 1
                selected_instances.append(query)
                for c in ['nb', 'lr']:
                    predicted_class = self.scores.loc[query, c + '_prediction']
                    predicted_class_index = np.where(
                        self.lr_class_labels == predicted_class)[0][0]
                    families_scores[c][predicted_class_index].set_value(
                        query, 'queried', True)
                self.scores.set_value(query, 'queried', True)
                lr_predicted_proba_df.set_value(query, 'queried', True)
                # Break condition - self.num_annotations instances have been queried
                if num_annotations >= self.num_annotations:
                    stop = True
                    break
        for instance_id in selected_instances:
            query = self.generateAnnotationQuery(instance_id, 0, None, None)
            self.annotation_queries.append(query)

    def generateLrPredictedProbaDataFrame(self):
        num_test_instances = self.datasets.test_instances.numInstances()
        lr_predicted_proba_df = pd.DataFrame(np.zeros((num_test_instances, len(self.lr_class_labels) + 1)),
                                             index=self.datasets.test_instances.ids.getIds(),
                                             columns=list(self.lr_class_labels) + ['queried'])
        if num_test_instances > 0:
            lr_predicted_proba_df.iloc[:, :-1] = self.lr_predicted_proba
            lr_predicted_proba_df['queried'] = [False] * num_test_instances
        return lr_predicted_proba_df

    def generateFamiliesScoresTables(self, classifier=None):
        if classifier is None:
            families_scores = {}
            families_scores['lr'] = self.generateFamiliesScoresTables('lr')
            families_scores['nb'] = self.generateFamiliesScoresTables('nb')
            return families_scores
        families_scores = []
        for i, family in enumerate(list(self.lr_class_labels)):
            selection = self.scores[classifier + '_prediction']
            if selection.shape[0] > 0:
                family_scores = self.scores.loc[self.scores[classifier +
                                                            '_prediction'] == family]
                family_scores = matrix_tools.sortDataFrame(
                    family_scores, classifier + '_score', True, False)
            else:
                family_scores = pd.DataFrame(
                    columns=self.scores.columns.values)
            families_scores.append(family_scores)
        return families_scores
