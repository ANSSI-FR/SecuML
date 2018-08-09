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

import numpy as np
from sklearn import semi_supervised
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import time

from SecuML.core.Classification.Classifier import Classifier
from SecuML.core.Classification.Monitoring.TrainingMonitoring import TrainingMonitoring


class LabelPropagation(Classifier):

    def createPipeline(self):
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', semi_supervised.LabelPropagation())])

    def training(self):
        start = time.time()
        self.pipeline.fit(self.datasets.train_instances.features.getValues(),
                          self.getSupervision(self.datasets.train_instances))
        self.training_execution_time = time.time() - start

        # Training monitoring
        # The model is trained on all the available data (labeled and unlabeled)
        # but the training monitoring is performed only on the labeled instances
        self.training_monitoring = TrainingMonitoring(self.conf,
                                                      self.datasets.getFeaturesNames(), monitoring_type='train')
        labeled_instances = self.datasets.train_instances.getAnnotatedInstances()
        if labeled_instances.numInstances() > 0:
            all_predicted_proba, predicted_proba, predicted_labels, predicted_scores = self.applyPipeline(
                labeled_instances.features.getValues())
            coefs = [0] * len(self.datasets.getFeaturesNames())
            self.training_monitoring.addFold(0, labeled_instances.getLabels(),
                                             labeled_instances.getFamilies(), labeled_instances.getIds(),
                                             all_predicted_proba, predicted_proba, predicted_scores, predicted_labels, coefs)
            self.displayMonitorings()
        if self.conf.families_supervision:
            self.class_labels = self.pipeline.named_steps['model'].classes_

    # The unspecified labels are represented with -1
    def getSupervision(self, instances, ground_truth=False):
        supervision = Classifier.getSupervision(
            self, instances, ground_truth=ground_truth)
        for i, s in enumerate(supervision):
            if s is None:
                supervision[i] = -1
            elif s:
                supervision[i] = 1
            else:
                supervision[i] = 0
        return supervision

    def applyPipeline(self, features):
        all_predicted_proba = self.pipeline.predict_proba(features)
        if self.conf.families_supervision:
            predicted_proba = None
        else:
            predicted_proba = all_predicted_proba[:, 1]
        predicted_labels = self.pipeline.predict(features)
        try:
            predicted_scores = self.pipeline.decision_function(features)
        except:
            predicted_scores = [0] * len(predicted_labels)
        # Predidcted labels: 0 -> False, 1 -> True
        predicted_labels = list(predicted_labels)
        for i, l in enumerate(predicted_labels):
            if l == 1:
                predicted_labels[i] = True
            elif l == 0:
                predicted_labels[i] = False
            else:
                raise ValueError()
        # Sometimes, LabelPropagation returns Nan predicted probas
        nan_index = np.argwhere(np.isnan(np.array(predicted_proba)))
        for i in nan_index:
            label = predicted_labels[i]
            if label:
                predicted_proba[i] = 1
            else:
                predicted_proba[i] = 0
        return all_predicted_proba, predicted_proba, predicted_labels, predicted_scores
