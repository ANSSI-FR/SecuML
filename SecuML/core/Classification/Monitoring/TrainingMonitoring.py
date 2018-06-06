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

from SecuML.core.Tools import dir_tools

from .Coefficients import Coefficients
from .FamiliesMonitoring import FamiliesMonitoring
from .PerformanceMonitoring import PerformanceMonitoring
from .PredictionsMonitoring import PredictionsMonitoring


class TrainingMonitoring(object):

    def __init__(self, conf):
        self.conf = conf
        self.monitoring_type = 'train'
        self.num_folds = 1

    def initMonitorings(self, datasets):
        self.performance_monitoring = PerformanceMonitoring(
            self.num_folds, self.conf)
        self.coefficients = None
        self.predictions_monitoring = None
        self.families_monitoring = None
        if not self.conf.families_supervision:
            self.coefficients = Coefficients(
                self.num_folds, datasets.getFeaturesNames())
            self.predictions_monitoring = PredictionsMonitoring(
                self.conf, True)
            if self.conf.getModelClassName() != 'Sssvdd':
                self.initFamiliesMonitoring(datasets)

    def initFamiliesMonitoring(self, datasets):
        self.families_monitoring = FamiliesMonitoring(datasets, 'train', False)

    def addFold(self, fold_id, predictions, coef):
        self.performance_monitoring.addFold(fold_id, predictions)
        if not self.conf.families_supervision:
            self.predictions_monitoring.addFold(predictions)
            self.coefficients.addFold(fold_id, coef)
            if self.families_monitoring is not None:
                self.families_monitoring.addFold(fold_id, predictions)

    def finalComputations(self):
        self.performance_monitoring.finalComputations()
        if not self.conf.families_supervision:
            self.predictions_monitoring.finalComputations()
            self.coefficients.finalComputations()
            if self.families_monitoring is not None:
                self.families_monitoring.finalComputations()

    def display(self, directory):
        training_dir = directory + self.monitoring_type + '/'
        dir_tools.createDirectory(training_dir)
        self.finalComputations()
        self.performance_monitoring.display(training_dir)
        if not self.conf.families_supervision:
            self.predictions_monitoring.display(training_dir)
            self.coefficients.display(training_dir)
            if self.families_monitoring is not None:
                families_dir = training_dir + 'families/'
                dir_tools.createDirectory(families_dir)
                self.families_monitoring.display(families_dir)
