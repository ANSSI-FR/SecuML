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

from ExecutionTimeMonitoring     import ExecutionTimeMonitoring
from FamiliesMonitoring          import FamiliesMonitoring
from LabelsMonitoring            import LabelsMonitoring
from ModelsPerformanceMonitoring import ModelsPerformanceMonitoring
from SuggestionsAccuracy         import SuggestionsAccuracy

class Monitoring(object):

    def __init__(self, iteration, validation_monitoring,
                 al_dir, iteration_dir):
        self.iteration = iteration
        self.datasets = iteration.datasets
        self.iteration_number = iteration.iteration_number
        self.validation_monitoring = validation_monitoring

        self.al_dir = al_dir
        self.iteration_dir = iteration_dir

        self.init()

    def init(self):
        self.labels_monitoring         = LabelsMonitoring(self)
        self.families_monitoring       = FamiliesMonitoring(self)
        self.execution_time_monitoring = ExecutionTimeMonitoring(self)
        self.suggestions               = SuggestionsAccuracy(self)

    def generateStartMonitoring(self):
        self.labels_monitoring.generateMonitoring()
        self.families_monitoring.generateMonitoring()
        if self.al_dir is not None:
            self.labels_monitoring.exportMonitoring()
            self.families_monitoring.exportMonitoring()

    def generateModelPerformanceMonitoring(self):
        self.models_performance = ModelsPerformanceMonitoring(
                self,
                self.validation_monitoring)
        self.models_performance.generateMonitoring()
        if self.al_dir is not None:
            self.models_performance.exportMonitoring()

    def generateEndMonitoring(self):
        self.execution_time_monitoring.generateMonitoring()
        self.suggestions.generateMonitoring()
        if self.al_dir is not None:
            self.execution_time_monitoring.exportMonitoring()
            self.suggestions.exportMonitoring()
