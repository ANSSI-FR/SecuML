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

import os.path as path

from .AlertsMonitoring import AlertsMonitoring
from .ExportClassifier import ExportClassifier

from SecuML.core.classification.monitoring.CvMonitoring import CvMonitoring
from SecuML.exp.Experiment import Experiment


class RunClassifier(object):

    def __init__(self, classifier, datasets, exp):
        self.classifier = classifier
        self.datasets = datasets
        self.exp = exp
        self.exp_conf = exp.exp_conf
        self.cv_test_methods = ['cv', 'temporal_cv', 'sliding_window']

    def run(self, cv_monitoring=False):
        test_conf = self.exp.exp_conf.core_conf.test_conf
        if test_conf.method in self.cv_test_methods:
            self.runCrossValidation(cv_monitoring=cv_monitoring)
        else:
            self.runOneFold(self.datasets, cv_monitoring=cv_monitoring)

    def runCrossValidation(self, cv_monitoring=False):
        test_conf = self.exp.exp_conf.core_conf.test_conf
        if test_conf.method in self.cv_test_methods:
            global_cv_monitoring = CvMonitoring(self.classifier.conf,
                                                num_folds=test_conf.num_folds)
            global_cv_monitoring.initMonitorings(self.datasets)
        else:
            global_cv_monitoring = None
        for fold_id, datasets in enumerate(self.datasets.datasets):
            self.runOneFold(datasets, fold_id=fold_id,
                            cv_monitoring=cv_monitoring)
            coefficients = None
            if not self.classifier.conf.families_supervision:
                coefficients = self.classifier.training_monitoring.coefficients.coef_summary['mean']
            if test_conf.method in self.cv_test_methods:
                global_cv_monitoring.addFold(fold_id,
                                             self.classifier.testing_predictions,
                                             coefficients)
        if test_conf.method in self.cv_test_methods:
            global_cv_monitoring.display(self.exp.output_dir())

    def trainTestValidation(self, datasets, fold_id, cv_monitoring=False):
        if self.exp.exp_conf.already_trained is not None:
            exp_dir = Experiment.get_output_dir(self.exp_conf.secuml_conf,
                                             self.exp_conf.dataset_conf.project,
                                             self.exp_conf.dataset_conf.dataset,
                                             self.exp_conf.already_trained)
            model_filename = path.join(exp_dir, 'model', 'model.out')
            self.classifier.loadModel(model_filename)
            self.classifier.testValidation(datasets)
        else:
            self.classifier.trainTestValidation(datasets,
                                                cv_monitoring=cv_monitoring)
        self.generateAlertsMonitoring(datasets, fold_id)

    def generateAlertsMonitoring(self, datasets, fold_id):
        self.exp.alerts = None
        # The alert analysis is not performed on each fold.
        if fold_id is not None:
            return
        core_conf = self.exp.exp_conf.core_conf
        alerts_conf = core_conf.test_conf.alerts_conf
        families_supervision = core_conf.classifier_conf.families_supervision
        if alerts_conf is None or families_supervision:
            return
        predictions = self.classifier.testing_monitoring.predictions_monitoring
        self.exp.alerts = AlertsMonitoring(self.exp, datasets, predictions)
        self.exp.alerts.groupAlerts()

    def export(self, fold_id):
        output_directory = self.exp.output_dir()
        if fold_id is not None:
            output_directory = path.join(output_directory, str(fold_id))
        export_classifier = ExportClassifier(self.classifier, output_directory,
                                             self.exp, self.exp.test_exp)
        export_classifier.export()

    def runOneFold(self, datasets, fold_id=None, cv_monitoring=False):
        self.trainTestValidation(datasets, fold_id, cv_monitoring=cv_monitoring)
        self.export(fold_id)
