## SecuML
## Copyright (C) 2016-2017  ANSSI
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


class Predictions(object):

    def __init__(self, predicted_proba_all, predicted_proba, predicted_labels,
                 predicted_scores):
        self.predicted_proba_all = predicted_proba_all
        self.predicted_proba = predicted_proba
        self.predicted_labels = predicted_labels
        self.predicted_scores = predicted_scores


class Classifier(object):

    def __init__(self, conf, datasets, cv_monitoring = False):
        self.conf = conf
        self.datasets = datasets
        self.cv_monitoring = cv_monitoring
        self.createPipeline()

    @abc.abstractmethod
    def createPipeline(self):
        return

    def run(self, output_directory, experiment):
        # Training
        self.training()
        self.exportTraining(output_directory)
        self.exportCrossValidation(output_directory)
        # Testing
        self.testing()
        self.exportTesting(output_directory)
        self.exportAlerts(experiment)
        # Validation
        if self.datasets.validation_instances is not None:
            self.validation()
            self.exportValidation(output_directory)

    def getSupervision(self, instances, true_labels = False):
        if self.conf.families_supervision:
            families = instances.getFamilies(true_labels = true_labels)
            return families
        else:
            labels = instances.getLabels(true_labels = true_labels)
            return labels

    def training(self):
        self.training_execution_time = 0
        start = time.time()
        self.cv = self.setBestParameters()
        self.training_execution_time += time.time() - start
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
        self.training_predictions = self.applyPipeline(self.datasets.train_instances.getFeatures())
        try:
            self.coefs = self.pipeline.named_steps['model'].coef_[0]
        except:
            self.coefs = [0] * len(self.datasets.getFeaturesNames())
        if self.conf.families_supervision:
            self.class_labels = self.pipeline.named_steps['model'].classes_

    def exportTraining(self, output_directory):
        self.training_monitoring = TrainingMonitoring(self.conf,
                self.datasets.getFeaturesNames(), monitoring_type = 'train')
        self.training_monitoring.addFold(0, self.datasets.train_instances.getLabels(),
                self.datasets.train_instances.getFamilies(),
                self.datasets.train_instances.getIds(),
                self.training_predictions, self.coefs)
        self.training_monitoring.display(output_directory)
        self.dumpModel(output_directory)

    def exportCrossValidation(self, output_directory):
        if self.cv_monitoring:
            self.crossValidationMonitoring()
            self.cv_monitoring.display(output_directory)
        else:
            self.cv_monitoring = None

    def crossValidationMonitoring(self):
        self.cv_monitoring = TrainingMonitoring(self.conf,
                                                self.datasets.getFeaturesNames(),
                                                monitoring_type = 'cv')
        cv_split = self.cv.split(self.datasets.train_instances.getFeatures(),
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
            cv_predictions = self.applyPipeline(test_instances.getFeatures())
            try:
                coefs = self.pipeline.named_steps['model'].coef_[0]
            except:
                coefs = [0] * len(self.datasets.getFeaturesNames())
            self.cv_monitoring.addFold(fold_id, test_instances.getLabels(),
                    test_instances.getFamilies(),
                    test_instances.getIds(), cv_predictions, coefs)

    def applyPipeline(self, features):
        if len(features) == 0:
            return Predictions([], [], [], [])
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
        predictions = Predictions(predicted_proba_all, predicted_proba,
                                  predicted_labels, predicted_scores)
        return predictions

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
        self.testing_predictions = self.applyPipeline(
                self.datasets.test_instances.getFeatures())
        self.testing_execution_time = time.time() - start

    def exportTesting(self, output_directory):
        if len(self.testing_predictions.predicted_labels) == 0:
            return
        self.testing_monitoring = TestingMonitoring(self.conf,
                self.datasets.test_instances.getLabels(true_labels = True),
                self.datasets.test_instances.getFamilies(true_labels = True))
        self.testing_monitoring.addPredictions(self.testing_predictions,
                                               self.datasets.test_instances.getIds())
        self.testing_monitoring.display(output_directory)

    def exportAlerts(self, experiment):
        self.displayAlerts(experiment)

    def validation(self):
        self.validation_predictions = self.applyPipeline(
                self.datasets.validation_instances.getFeatures())

    def exportValidation(self, output_directory):
        self.validation_monitoring = TestingMonitoring(self.conf,
                self.datasets.validation_instances.getLabels(true_labels = True),
                self.datasets.validation_instances.getFamilies(true_labels = True),
                monitoring_type = 'validation')
        self.validation_monitoring.addPredictions(self.validation_predictions,
                                                  self.datasets.validation_instances.getIds())
        self.validation_monitoring.display(output_directory)

    def displayAlerts(self, experiment):
        if self.conf.families_supervision:
            return
        if self.conf.test_conf.alerts_conf is None:
            return
        predictions = self.testing_monitoring.predictions_monitoring
        alerts = AlertsMonitoring(self.datasets, predictions, experiment)
        alerts.generateAlerts(experiment.getOutputDirectory())

    def dumpModel(self, output_directory):
        model_dir = output_directory + 'model/'
        dir_tools.createDirectory(model_dir)
        joblib.dump(self.pipeline, model_dir + 'model.out')
