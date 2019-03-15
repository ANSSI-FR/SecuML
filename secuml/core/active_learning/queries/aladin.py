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
import pandas as pd
from sqlalchemy.sql.expression import false
import time

from secuml.core.classif.classifiers.gaussian_naive_bayes \
        import GaussianNaiveBayes
from secuml.core.clustering.monitoring.perf_indicators \
        import PerformanceIndicators
from secuml.core.tools.matrix import sort_data_frame
from secuml.core.tools.core_exceptions import SecuMLcoreException

from . import Queries


class AladinAtLeastTwoFamilies(SecuMLcoreException):

    def __str__(self):
        return('Aladin requires that the initial annotated dataset '
               'contains at least two different families.')


class AladinQueries(Queries):

    def __init__(self, iteration, conf):
        Queries.__init__(self, iteration)
        self.num_annotations = conf.num_annotations
        self.conf = conf
        datasets = self.iteration.datasets
        self.train_instances = datasets.instances.get_annotated_instances()
        self.test_instances = datasets.get_unlabeled_instances()
        self.check_input_data()

    def run_models(self):
        self._run_logistic_regression()
        self._run_naive_bayes()

    def generate_queries(self, already_queried=None):
        self.compute_scores()
        self._gen_queries_from_scores()

    def check_input_data(self):
        families = set(self.train_instances.annotations.get_families())
        if len(families) < 2:
            raise AladinAtLeastTwoFamilies()

    def _run_logistic_regression(self):
        return None

    def _run_naive_bayes(self):
        naive_bayes_conf = self._create_naive_bayes_conf()
        # Update training data
        # the naive Bayes classifier is trained on all the data
        self.test_instances.annotations.set_families(
                list(self.lr_predicted_labels))
        train_instances = copy.deepcopy(self.train_instances)
        train_instances.union(self.test_instances)
        self.eval_clustering_perf(train_instances)
        # Train the naive Bayes detection model and predict
        self.naive_bayes = GaussianNaiveBayes(naive_bayes_conf)
        _, self.nb_time = self.naive_bayes.training(train_instances)
        num_test_instances = self.test_instances.num_instances()
        self.test_instances.annotations.set_families(
                                [None for i in range(num_test_instances)])
        start_time = time.time()
        if num_test_instances == 0:
            self.nb_predicted_labels = []
        else:
            self.nb_predicted_labels = self.naive_bayes.pipeline.predict(
                self.test_instances.features.get_values())
        self.nb_time += time.time() - start_time
        self.nb_class_labels = self.naive_bayes.class_labels

    def eval_clustering_perf(self, instances):
        self.clustering_perf = PerformanceIndicators()
        self.clustering_perf.gen_eval(instances.ground_truth.get_families(),
                                      instances.annotations.get_families())

    def compute_scores(self):
        self._create_scores_df()
        self._compute_uncertainty_scores()
        self._compute_anomalous_scores()

    def _create_scores_df(self):
        num_test_instances = self.test_instances.num_instances()
        header = ['lr_prediction', 'lr_score', 'nb_prediction', 'nb_score',
                  'queried']
        self.scores = pd.DataFrame(np.zeros((num_test_instances, len(header))),
                                   index=self.test_instances.ids.get_ids(),
                                   columns=header)
        self.scores['queried'] = [False] * num_test_instances

    # Uncertain instances have a low difference between the probability of
    # belonging to the most likely family and the second most likely family.
    # In Aladin, the authors consider this measure of uncertainty instead of
    # the entropy used by Pelleg and Moore (Active Learning for Anomaly and
    # Rare-Category Detection).
    def _compute_uncertainty_scores(self):
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

    # Anomalous instances have a low probability of belonging to the assigned
    # family
    def _compute_anomalous_scores(self):
        self.scores['nb_prediction'] = self.nb_predicted_labels
        for c in set(self.nb_predicted_labels):
            selection = self.scores['nb_prediction'] == c
            c_ids = self.scores.loc[selection].index.values
            c_instances = self.test_instances.get_from_ids(c_ids)
            c_features = c_instances.features.values
            c_likelihood = self.naive_bayes.log_likelihood(c_features, c)
            self.scores.loc[selection, 'nb_score'] = c_likelihood

    def _gen_queries_from_scores(self):
        assert(np.array_equal(self.lr_class_labels, self.nb_class_labels))
        lr_predicted_proba_df = self.gen_lr_predicted_proba_df()
        num_families = len(self.lr_class_labels)
        self.annotation_queries = []

        # There are fewer annotation queries than the number of families
        if self.num_annotations <= num_families:
            if self.iteration.iter_num % 2 == 0:
                classifier = 'lr'
            else:
                classifier = 'nb'
            sort_data_frame(self.scores, '%s_score' % classifier, True, True)
            selected_instances = self.scores.index.tolist()[
                :self.num_annotations]
            for instance_id in selected_instances:
                query = self.generate_query(instance_id, 0, None, None)
                self.add_query(query)
            return

        # Otherwise
        num_uncertain = [0] * num_families
        num_anomalous = [0] * num_families
        families_scores = self._gen_families_scores_tables()
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
                selected_rows = scores.loc[scores['queried'] == false()]
                if len(selected_rows) > 0:
                    query = selected_rows.index.tolist()[0]
                else:
                    # No anomalous or uncertain instances available for
                    # annotation
                    # Select the most likely instance according to the
                    # logistic regression output
                    self.conf.logger.debug(
                        family + ': no anomalous, no uncertain instances')
                    selected_rows = lr_predicted_proba_df.loc[
                                            lr_predicted_proba_df['queried'] ==
                                            false()]
                    selected_rows = sort_data_frame(selected_rows, family,
                                                    False, False)
                    selection = selected_rows.index.tolist()
                    # Break condition
                    # There is no instance left in the unlabelled pool
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
                # Break condition
                # self.num_annotations instances have been queried
                if num_annotations >= self.num_annotations:
                    stop = True
                    break
        for instance_id in selected_instances:
            query = self.generate_query(instance_id, 0, None, None)
            self.add_query(query)

    def gen_lr_predicted_proba_df(self):
        num_test_instances = self.test_instances.num_instances()
        lr_predicted_proba_df = pd.DataFrame(
                np.zeros((num_test_instances, len(self.lr_class_labels) + 1)),
                index=self.test_instances.ids.get_ids(),
                columns=list(self.lr_class_labels) + ['queried'])
        if num_test_instances > 0:
            lr_predicted_proba_df.iloc[:, :-1] = self.lr_predicted_proba
            lr_predicted_proba_df['queried'] = [False] * num_test_instances
        return lr_predicted_proba_df

    def _gen_families_scores_tables(self, classifier=None):
        if classifier is None:
            families_scores = {}
            families_scores['lr'] = self._gen_families_scores_tables('lr')
            families_scores['nb'] = self._gen_families_scores_tables('nb')
            return families_scores
        families_scores = []
        for i, family in enumerate(list(self.lr_class_labels)):
            selection = self.scores[classifier + '_prediction']
            if selection.shape[0] > 0:
                family_scores = self.scores.loc[
                        self.scores[classifier + '_prediction'] == family]
                family_scores = sort_data_frame(family_scores,
                                                '%s_score' % classifier,
                                                True, False)
            else:
                col_values = self.scores.columns.values
                family_scores = pd.DataFrame(columns=col_values)
            families_scores.append(family_scores)
        return families_scores
