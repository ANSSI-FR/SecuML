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

from SecuML.core.tools import dir_tools

from .PerformanceMonitoring import PerformanceMonitoring
from .PredictionsMonitoring import PredictionsMonitoring


class TestingMonitoring(object):

    def __init__(self, conf, monitoring_type='test'):
        self.conf = conf
        self.monitoring_type = monitoring_type

    def setHasGroundTruth(self, datasets):
        if self.monitoring_type == 'test':
            instances = datasets.test_instances
        elif self.monitoring_type == 'validation':
            instances = datasets.validation_instances
        labels = instances.ground_truth.getLabels()
        self.has_ground_truth = all(l is not None for l in labels)

    def initMonitorings(self, datasets):
        self.setHasGroundTruth(datasets)
        self.predictions_monitoring = PredictionsMonitoring(self.conf,
                                                          self.has_ground_truth)
        self.performance_monitoring = None
        if self.has_ground_truth:
            self.performance_monitoring = PerformanceMonitoring(1, self.conf)

    def addPredictions(self, predictions):
        if self.has_ground_truth:
            self.performance_monitoring.addFold(0, predictions)
        self.predictions_monitoring.addFold(predictions)

    def finalComputations(self):
        self.predictions_monitoring.finalComputations()
        if self.has_ground_truth:
            self.performance_monitoring.finalComputations()

    def display(self, directory):
        testing_dir = path.join(directory, self.monitoring_type)
        dir_tools.createDirectory(testing_dir)
        self.finalComputations()
        self.predictions_monitoring.display(testing_dir)
        if self.has_ground_truth:
            self.performance_monitoring.display(testing_dir)

    def getPredictedLabels(self):
        return self.predictions_monitoring.getPredictedLabels()

    def getAllPredictedProba(self):
        return self.predictions_monitoring.getAllPredictedProba()
