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

from secuml.core.classif.monitoring.perf import PerformanceMonitoring
from secuml.core.classif.monitoring.prediction import PredictionsMonitoring
from secuml.core.classif.monitoring.test import TestMonitoring \
        as TestMonitoringCore
from secuml.core.classif.monitoring.train import TrainMonitoring \
        as TrainMonitoringCore

from .alerts import AlertsMonitoring
from .coeff import Coefficients


class TrainMonitoring(TrainMonitoringCore):

    def __init__(self, exp, exec_time):
        TrainMonitoringCore.__init__(self, exp.exp_conf.core_conf, exec_time)
        self.exp = exp

    def init(self, features_ids):
        self.performance = PerformanceMonitoring(self.num_folds, self.conf)
        self.predictions = PredictionsMonitoring(self.conf, True)
        self.coefficients = None
        if self.interpretation:
            self.coefficients = Coefficients(self.num_folds, features_ids,
                                             self.conf, self.exp.session)


class TestMonitoring(TestMonitoringCore):

    def __init__(self, exp, classifier_conf, exec_time, alerts_conf=None):
        TestMonitoringCore.__init__(self, classifier_conf, exec_time)
        self.exp = exp
        self.alerts_monitoring = None
        if alerts_conf is not None:
            self.alerts_monitoring = AlertsMonitoring(self.exp, alerts_conf)

    def final_computations(self):
        TestMonitoringCore.final_computations(self)
        if self.alerts_monitoring is not None:
            self.alerts_monitoring.extract(self.predictions)
            self.alerts_monitoring.group()

    def display(self, directory):
        TestMonitoringCore.display(self, directory)
        if self.alerts_monitoring is not None:
            self.alerts_monitoring.display(directory)


class CvMonitoring(TrainMonitoring):

    def __init__(self, exp, num_folds, classifier_conf):
        TrainMonitoringCore.__init__(self, classifier_conf, 0)
        self.exp = exp
        self.monitoring_type = 'cv'
        self.num_folds = num_folds
