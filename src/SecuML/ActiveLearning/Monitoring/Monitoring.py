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

from ExecutionTimeMonitoring     import ExecutionTimeMonitoring
from FamiliesMonitoring          import FamiliesMonitoring
from LabelsMonitoring            import LabelsMonitoring
from ModelsPerformanceMonitoring import ModelsPerformanceMonitoring
from SuggestionsAccuracy         import SuggestionsAccuracy

class Monitoring(object):

    def __init__(self, datasets, experiment, iteration, validation_monitoring):
        self.datasets = datasets
        self.experiment = experiment
        self.iteration = iteration
        self.iteration_number = iteration.iteration_number
        self.setDirectories()
        self.init()
        self.validation_monitoring = validation_monitoring

    def init(self):
        self.labels_monitoring         = LabelsMonitoring(self)
        self.families_monitoring       = FamiliesMonitoring(self)
        self.execution_time_monitoring = ExecutionTimeMonitoring(self)
        self.suggestions               = SuggestionsAccuracy(self)

    def setDirectories(self):
        self.AL_directory = self.experiment.getOutputDirectory()
        self.iteration_dir  = self.AL_directory
        self.iteration_dir += str(self.iteration_number) + '/'

    def generateStartMonitoring(self):
        self.labels_monitoring.generateMonitoring()
        self.families_monitoring.generateMonitoring()

    def generateModelPerformanceMonitoring(self):
        self.models_performance = ModelsPerformanceMonitoring(self,
                self.validation_monitoring)
        self.models_performance.generateMonitoring()

    def generateEndMonitoring(self):
        self.execution_time_monitoring.generateMonitoring()
        self.suggestions.generateMonitoring()
