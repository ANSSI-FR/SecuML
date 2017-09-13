## SecuML
## Copyright (C) 2016  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

import abc
import time

from sklearn.externals import joblib
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import GridSearchCV

from SecuML.Tools import dir_tools

from Monitoring.AlertsMonitoring import AlertsMonitoring
from Monitoring.TestingMonitoring import TestingMonitoring
from Monitoring.TrainingMonitoring import TrainingMonitoring

class Classifier(object):

    def __init__(self, experiment, datasets, cv_monitoring = False):
        self.experiment = experiment
        self.conf = experiment.classification_conf
        self.datasets = datasets
        self.cv_monitoring = cv_monitoring
        self.setOutputDirectory()
        self.createPipeline()

    @abc.abstractmethod
    def createPipeline(self):
        return

    def run(self):
        self.training()
        self.testing()
        if self.datasets.validation_instances is not None:
            self.validation()

    def setOutputDirectory(self):
        self.output_directory = self.experiment.getOutputDirectory()

    def getSupervision(self, instances, true_labels = False):
        if self.conf.families_supervision:
            families = instances.getFamilies(true_labels = true_labels)
            return families
        else:
            labels = instances.getLabels(true_labels = true_labels)
            return labels

    def training(self):
        self.training_execution_time = 0
        self.training_monitoring = TrainingMonitoring(self.conf,
                self.datasets.getFeaturesNames(), monitoring_type = 'train')
        start = time.time()
        cv = self.setBestParameters()
        self.training_execution_time += time.time() - start
        if self.cv_monitoring:
            self.crossValidationMonitoring(cv)
        else:
            self.cv_monitoring = None
        start = time.time()
        if self.datasets.sample_weight:
            self.pipeline.fit(self.datasets.train_instances.getFeatures(),
                    self.getSupervision(self.datasets.train_instances),
                    **{'model__sample_weight': self.datasets.sample_weight})
        else:
            self.pipeline.fit(self.datasets.train_instances.getFeatures(),
                    self.getSupervision(self.datasets.train_instances))
        self.training_execution_time += time.time() - start
        # Training monitoring
        predicted_proba_all, predicted_proba, predicted_labels, predicted_scores = \
                self.applyPipeline(self.datasets.train_instances.getFeatures())
        try:
            coefs = self.pipeline.named_steps['model'].coef_[0]
        except:
            coefs = [0] * len(self.datasets.getFeaturesNames())
        self.training_monitoring.addFold(0, self.datasets.train_instances.getLabels(),
                self.datasets.train_instances.getFamilies(), self.datasets.train_instances.getIds(),
                predicted_proba_all, predicted_proba, predicted_scores, predicted_labels, coefs)
        self.displayMonitorings()
        if self.conf.families_supervision:
            self.class_labels = self.pipeline.named_steps['model'].classes_

    def applyPipeline(self, features):
        if len(features) == 0:
            return [], [], [], []
        predicted_proba_all = self.pipeline.predict_proba(features)
        if self.conf.families_supervision:
            predicted_proba = None
        else:
            predicted_proba = predicted_proba_all[:, 1]
        predicted_labels    = self.pipeline.predict(features)
        try:
            predicted_scores = self.pipeline.decision_function(features)
        except:
            predicted_scores = [0] * len(predicted_labels)
        return predicted_proba_all, predicted_proba, predicted_labels, predicted_scores

    def displayMonitorings(self):
        self.training_monitoring.display(self.output_directory)
        if self.cv_monitoring is not None:
            self.cv_monitoring.display(self.output_directory)
        self.dumpModel()

    def crossValidationMonitoring(self, cv):
        self.cv_monitoring = TrainingMonitoring(self.conf, self.datasets.getFeaturesNames(), monitoring_type = 'cv')
        cv_split = cv.split(
                self.datasets.train_instances.getFeatures(),
                self.getSupervision(self.datasets.train_instances))
        for fold_id, (train, test) in enumerate(cv_split):
            train_ids = [self.datasets.train_instances.ids[i] for i in train]
            test_ids = [self.datasets.train_instances.ids[i] for i in test]
            sample_weight = self.datasets.sample_weight
            if sample_weight is not None:
                sample_weight = [sample_weight[i] \
                        for i in range(self.datasets.train_instances.numInstances()) if i in train]
            train_instances = self.datasets.train_instances.getInstancesFromIds(train_ids)
            test_instances  = self.datasets.train_instances.getInstancesFromIds(test_ids)
            if self.datasets.sample_weight:
                self.pipeline.fit(train_instances.getFeatures(),
                        self.getSupervision(train_instances),
                        **{'model__sample_weight': sample_weight})
            else:
                self.pipeline.fit(train_instances.getFeatures(),
                        self.getSupervision(train_instances))
            predicted_proba_all, predicted_proba, predicted_labels, predicted_scores = \
                    self.applyPipeline(test_instances.getFeatures())
            try:
                coefs = self.pipeline.named_steps['model'].coef_[0]
            except:
                coefs = [0] * len(self.datasets.getFeaturesNames())
            self.cv_monitoring.addFold(fold_id, test_instances.getLabels(), test_instances.getFamilies(),
                    test_instances.getIds(), predicted_proba_all, predicted_proba, predicted_scores,
                    predicted_labels, coefs)

    def setBestParameters(self):
        cv = StratifiedKFold(n_splits = self.conf.num_folds)
        param_grid = self.conf.getParamGrid()
        if param_grid is None:
            # No parameter value to select
            return
        if self.conf.families_supervision:
            scoring = 'f1_macro'
        else:
            scoring = 'roc_auc'
        grid_search = GridSearchCV(self.pipeline, param_grid = param_grid,
                scoring = scoring,
                cv = cv,
                n_jobs = -1,
                fit_params = {'model__sample_weight': self.datasets.sample_weight})
        grid_search.fit(self.datasets.train_instances.getFeatures(),
                self.getSupervision(self.datasets.train_instances))
        self.conf.setBestValues(grid_search)
        self.pipeline.set_params(**self.conf.getBestValues())
        return cv

    def testing(self):
        start = time.time()
        predicted_proba_all, predicted_proba, predicted_labels, predicted_scores = \
                self.applyPipeline(self.datasets.test_instances.getFeatures())
        self.testing_execution_time = time.time() - start
        if len(predicted_labels) > 0:
            self.testing_monitoring = TestingMonitoring(self.conf,
                    self.datasets.test_instances.getLabels(true_labels = True),
                    self.datasets.test_instances.getFamilies(true_labels = True))
            self.testing_monitoring.addPredictions(predicted_proba_all, predicted_proba, predicted_scores,
                    predicted_labels, self.datasets.test_instances.getIds())
            self.testing_monitoring.display(self.output_directory)
            self.displayAlerts()

    def validation(self):
        predicted_proba_all, predicted_proba, predicted_labels, predicted_scores = \
                self.applyPipeline(self.datasets.validation_instances.getFeatures())
        self.validation_monitoring = TestingMonitoring(self.conf,
                self.datasets.validation_instances.getLabels(true_labels = True),
                self.datasets.validation_instances.getFamilies(true_labels = True),
                monitoring_type = 'validation')
        self.validation_monitoring.addPredictions(predicted_proba_all, predicted_proba, predicted_scores,
                predicted_labels, self.datasets.validation_instances.getIds())
        self.validation_monitoring.display(self.output_directory)

    def displayAlerts(self):
        if self.conf.families_supervision:
            return
        if self.experiment.classification_conf.test_conf.alerts_conf is None:
            return
        predictions = self.testing_monitoring.predictions_monitoring
        alerts = AlertsMonitoring(self.datasets, predictions, self.experiment)
        alerts.generateAlerts(self.output_directory)

    def dumpModel(self):
        model_dir = self.output_directory + 'model/'
        dir_tools.createDirectory(model_dir)
        joblib.dump(self.pipeline, model_dir + 'model.out')
