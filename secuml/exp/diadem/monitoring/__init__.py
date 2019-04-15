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

import os

from secuml.core.classif.monitoring.perf import PerformanceMonitoring

from .alerts import AlertsMonitoring
from .classifier import ClassifierMonitoring
from .prediction import PredictionsMonitoring


class TrainMonitoring(ClassifierMonitoring):

    def __init__(self, exp):
        ClassifierMonitoring.__init__(self, exp)
        self.cv_monitoring = None

    def set_cv_monitoring(self, cv_monitoring):
        self.cv_monitoring = cv_monitoring

    def display(self, output_dir):
        ClassifierMonitoring.display(self, output_dir)
        if self.cv_monitoring is not None:
            cv_dir = os.path.join(output_dir, 'cv')
            os.mkdir(cv_dir)
            self.cv_monitoring.display(cv_dir)


class DetectionMonitoring(object):

    def __init__(self, exp, alerts_conf=None):
        self.exp = exp
        self.exec_time = 0
        self.alerts_monitoring = None
        if alerts_conf is not None:
            self.alerts_monitoring = AlertsMonitoring(self.exp, alerts_conf)
        self.predictions = PredictionsMonitoring(self.exp)
        self.performance = None
        self.has_ground_truth = self.exp.has_ground_truth()
        if self.has_ground_truth:
            self.performance = PerformanceMonitoring()

    def add_predictions(self, predictions, exec_time):
        self.exec_time += exec_time
        if self.performance is not None:
            self.performance.add_fold(predictions)
        self.predictions.add_fold(predictions)

    def final_computations(self):
        self.predictions.final_computations()
        if self.performance is not None:
            self.performance.final_computations()
        if self.alerts_monitoring is not None:
            self.alerts_monitoring.group(self.predictions.predictions)

    def display(self, directory):
        self.final_computations()
        self.predictions.display(directory)
        if self.performance is not None:
            self.performance.display(directory)
        if self.alerts_monitoring is not None:
            self.alerts_monitoring.display(directory)


class CvMonitoring(object):

    def __init__(self, exp, num_folds):
        self.num_folds = num_folds
        self.classifiers = ClassifierMonitoring(exp, num_folds=num_folds)
        self.detect_monitoring = DetectionMonitoring(exp)

    def add_fold(self, classifier, train_exec_time, predictions,
                 pred_exec_time, fold_id):
        self.classifiers.set_classifier(classifier, train_exec_time,
                                        fold_id=fold_id)
        self.detect_monitoring.add_predictions(predictions, pred_exec_time)

    def final_computations(self):
        self.classifiers.final_computations()
        self.detect_monitoring.final_computations()

    def display(self, directory):
        self.classifiers.display(directory)
        self.detect_monitoring.display(directory)
