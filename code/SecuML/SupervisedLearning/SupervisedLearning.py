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
from SecuML.Tools import matrix_tools

from Monitoring.AlertsMonitoring import AlertsMonitoring
from Monitoring.TestingMonitoring import TestingMonitoring
from Monitoring.TrainingMonitoring import TrainingMonitoring

class SupervisedLearning(object):

    def __init__(self, experiment, datasets, output_directory = None,
            cv_monitoring = False):
        self.experiment = experiment
        self.conf = experiment.supervised_learning_conf
        self.datasets = datasets
        self.cv_monitoring = cv_monitoring
        self.setOutputDirectory(output_directory)
        self.createPipeline()

    @abc.abstractmethod
    def createPipeline(self):
        return

    def run(self):
        self.training()
        self.testing()
        self.validation()

    def setOutputDirectory(self, output_directory):
        if output_directory is None:
            self.output_directory = dir_tools.getExperimentOutputDirectory(
                    self.experiment)
        else:
            self.output_directory = output_directory

    def training(self):
        self.training_execution_time = 0
        self.training_monitoring = TrainingMonitoring(self.conf,
                self.datasets.getFeaturesNames(), monitoring_type = 'train')
        start = time.time()
        cv = StratifiedKFold(n_splits = self.conf.num_folds)
        self.setBestParameters(cv)
        self.training_execution_time += time.time() - start
        if self.cv_monitoring:
            self.crossValidationMonitoring()
        else:
            self.cv_monitoring = None
        start = time.time()
        self.pipeline.fit(self.datasets.train_instances.getFeatures(),
                self.datasets.train_instances.getLabels(),
                **{'model__sample_weight': self.datasets.sample_weight})
        self.training_execution_time += time.time() - start
        predicted_proba  = self.pipeline.predict_proba(self.datasets.train_instances.getFeatures())[:, 1]
        predicted_scores = self.pipeline.decision_function(self.datasets.train_instances.getFeatures())
        try:
            coefs = self.pipeline.named_steps['model'].coef_[0]
        except:
            coefs = [0] * len(self.datasets.getFeaturesNames())
        self.training_monitoring.addFold(0, self.datasets.train_instances.getLabels(),
                self.datasets.train_instances.getSublabels(), self.datasets.train_instances.getIds(),
                predicted_proba, predicted_scores, coefs)
        self.displayMonitorings()

    def displayMonitorings(self):
        self.training_monitoring.display(self.output_directory)
        if self.cv_monitoring is not None:
            self.cv_monitoring.display(self.output_directory)
        self.dumpModel()

    def crossValidationMonitoring(self):
        self.cv_monitoring = TrainingMonitoring(self.conf,
                self.datasets.getFeaturesNames(), monitoring_type = 'cv')
        cv_split = cv.split(
                self.datasets.train_instances.getFeatures(),
                self.datasets.train_instances.getLabels())
        for fold_id, (train, test) in enumerate(cv_split):
            train_ids = [self.datasets.train_instances.ids[i] for i in train]
            test_ids = [self.datasets.train_instances.ids[i] for i in test]
            sample_weight = self.datasets.sample_weight
            if sample_weight is not None:
                sample_weight = [sample_weight[i] \
                        for i in range(self.datasets.train_instances.numInstances()) if i in train]
            train_instances = self.datasets.train_instances.getInstancesFromIds(train_ids)
            test_instances = self.datasets.train_instances.getInstancesFromIds(test_ids)
            self.pipeline.fit(train_instances.getFeatures(), train_instances.getLabels(),
                    **{'model__sample_weight' : sample_weight})
            predicted_proba_fold = self.pipeline.predict_proba(test_instances.getFeatures())[:,1]
            try:
                coefs = self.pipeline.named_steps['model'].coef_[0]
            except:
                coefs = [0] * len(self.datasets.getFeaturesNames())
            self.cv_monitoring.addFold(fold_id, test_instances.getLabels(), test_instances.getSublabels(),
                    test_instances.getIds(), predicted_proba_fold, coefs)

    def setBestParameters(self, cv):
        param_grid = self.conf.getParamGrid()
        grid_search = GridSearchCV(self.pipeline, param_grid = param_grid,
                scoring = 'roc_auc',
                cv = cv,
                n_jobs = -1,
                fit_params = {'model__sample_weight': self.datasets.sample_weight})
        grid_search.fit(self.datasets.train_instances.getFeatures(),
                self.datasets.train_instances.getLabels())
        self.conf.setBestValues(grid_search)
        self.pipeline.set_params(**self.conf.getBestValues())

    def testing(self):
        self.testing_execution_time = 0
        start = time.time()
        predicted_proba = self.pipeline.predict_proba(self.datasets.test_instances.getFeatures())[:,1]
        self.testing_execution_time += time.time() - start
        predicted_scores = self.pipeline.decision_function(self.datasets.test_instances.getFeatures())
        self.testing_monitoring = TestingMonitoring(self.datasets.test_instances.getLabels(true_labels = True),
                self.datasets.test_instances.getSublabels(true_labels = True))
        self.testing_monitoring.addPredictions(predicted_proba, predicted_scores, 
                self.datasets.test_instances.getIds())
        self.testing_monitoring.display(self.output_directory)
        self.displayAlerts()

    def validation(self):
        if self.datasets.validation_instances is None:
            return
        predicted_proba  = self.pipeline.predict_proba(self.datasets.validation_instances.getFeatures())[:,1]
        predicted_scores = self.pipeline.decision_function(self.datasets.validation_instances.getFeatures())
        self.validation_monitoring = TestingMonitoring(self.datasets.validation_instances.getLabels(
            true_labels = True),
                self.datasets.validation_instances.getSublabels(true_labels = True), 
                monitoring_type = 'validation')
        self.validation_monitoring.addPredictions(predicted_proba, predicted_scores,
                self.datasets.validation_instances.getIds())
        self.validation_monitoring.display(self.output_directory)

    def displayAlerts(self):
        if self.experiment.supervised_learning_conf.test_conf.alerts_conf is None:
            return
        predictions = self.testing_monitoring.predictions_monitoring
        alerts = AlertsMonitoring(self.datasets, predictions, self.experiment)
        alerts.generateAlerts(self.output_directory)

    def dumpModel(self):
        model_dir = self.output_directory + 'model/'
        dir_tools.createDirectory(model_dir)
        joblib.dump(self.pipeline, model_dir + 'model.out')
