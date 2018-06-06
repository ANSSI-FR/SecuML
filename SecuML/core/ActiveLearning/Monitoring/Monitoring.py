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

from .ExecutionTimeMonitoring import ExecutionTimeMonitoring
from .LabelsMonitoring import LabelsMonitoring
from .ModelsPerformanceMonitoring import ModelsPerformanceMonitoring
from .SuggestionsAccuracy import SuggestionsAccuracy


class Monitoring(object):

    def __init__(self, iteration):
        self.iteration = iteration
        self.datasets = iteration.datasets
        self.iteration_number = iteration.iteration_number
        self.validation_monitoring = iteration.conf.validation_conf is not None
        self.init()

    def init(self):
        self.labels_monitoring = LabelsMonitoring(self)
        self.execution_time_monitoring = ExecutionTimeMonitoring(self)
        self.suggestions = SuggestionsAccuracy(self)

    def generateStartMonitoring(self):
        self.labels_monitoring.generateMonitoring()

    def generateModelPerformanceMonitoring(self):
        self.models_performance = ModelsPerformanceMonitoring(
            self,
            self.validation_monitoring)
        self.models_performance.generateMonitoring()

    def generateEndMonitoring(self):
        self.execution_time_monitoring.generateMonitoring()
        self.suggestions.generateMonitoring()

    def exportStartMonitoring(self, al_dir, iteration_dir):
        self.labels_monitoring.exportMonitoring(al_dir, iteration_dir)

    def exportModelPerformanceMonitoring(self, al_dir, iteration_dir):
        self.models_performance.exportMonitoring(al_dir, iteration_dir)

    def exportExecutionTimeMonitoring(self, al_dir, iteration_dir):
        self.execution_time_monitoring.exportMonitoring(al_dir, iteration_dir)

    def exportEndMonitoring(self, al_dir, iteration_dir):
        self.suggestions.exportMonitoring(al_dir, iteration_dir)
