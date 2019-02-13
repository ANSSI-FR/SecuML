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

from .performance import PerformanceMonitoring
from .prediction import PredictionsMonitoring


class TestMonitoring(object):

    def __init__(self, conf, exec_time, monitoring_type='test'):
        self.conf = conf
        self.exec_time = exec_time
        self.monitoring_type = monitoring_type

    def init(self, instances):
        self.has_ground_truth = instances.has_ground_truth()
        self.predictions = PredictionsMonitoring(self.conf,
                                                 self.has_ground_truth)
        self.performance = None
        if self.has_ground_truth:
            self.performance = PerformanceMonitoring(1, self.conf)

    def add_predictions(self, predictions):
        if self.performance is not None:
            self.performance.add_fold(0, predictions)
        self.predictions.add_fold(predictions)

    def final_computations(self):
        self.predictions.final_computations()
        if self.performance is not None:
            self.performance.final_computations()

    def display(self, directory):
        self.final_computations()
        self.predictions.display(directory)
        if self.performance is not None:
            self.performance.display(directory)
