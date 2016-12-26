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

import time

from SecuML.ActiveLearning.Monitoring.ClusteringEvaluationMonitoring \
        import ClusteringEvaluationMonitoring
from SecuML.ActiveLearning.Monitoring.ExecutionTimeMonitoring \
        import ExecutionTimeMonitoring
from SecuML.ActiveLearning.Monitoring.LabelsMonitoring \
        import LabelsMonitoring
from SecuML.ActiveLearning.Monitoring.SublabelsMonitoring \
        import SublabelsMonitoring
from SecuML.ActiveLearning.Monitoring.ValidationMonitoring \
        import ValidationMonitoring

from SecuML.Tools import dir_tools

class Monitoring(object):

    def __init__(self, datasets, experiment, iteration,
            validation_monitoring):
        self.datasets = datasets
        self.experiment = experiment
        self.iteration = iteration
        self.iteration_number = iteration.iteration_number
        self.validation_monitoring = validation_monitoring
        self.ilab = experiment.labeling_method == 'ILAB'
        self.init()

    def init(self):
        self.AL_directory = dir_tools.getExperimentOutputDirectory(
                self.experiment)
        self.iteration_dir  = self.AL_directory
        self.iteration_dir += str(self.iteration_number) + '/'
        self.labels_monitoring = LabelsMonitoring(self)
        self.sublabels_monitoring = SublabelsMonitoring(self)
        self.execution_time_monitoring = ExecutionTimeMonitoring(self)
        if self.validation_monitoring:
            self.validation_monitoring = ValidationMonitoring(self)
        else:
            self.validation_monitoring = None

    def iterationMonitoring(self):
        print 'iterationMonitoring'
        start_time = time.time()
        self.labels_monitoring.iterationMonitoring()
        print 'labels_monitoring', time.time() - start_time
        start_time = time.time()
        self.sublabels_monitoring.iterationMonitoring()
        print 'sublabels_monitoring', time.time() - start_time
        if self.validation_monitoring is not None:
            start_time = time.time()
            self.validation_monitoring.iterationMonitoring()
            print 'validation_monitoring', time.time() - start_time

    def evolutionMonitoring(self):
        print 'evolutionMonitoring'
        start_time = time.time()
        self.labels_monitoring.evolutionMonitoring()
        print 'labels_monitoring', time.time() - start_time
        start_time = time.time()
        self.sublabels_monitoring.evolutionMonitoring()
        print 'sublabels_monitoring', time.time() - start_time
        if self.validation_monitoring is not None:
            start_time = time.time()
            self.validation_monitoring.evolutionMonitoring()
            print 'validation_monitoring', time.time() - start_time

    def generateExecutionTimeMonitoring(self):
        self.execution_time_monitoring.iterationMonitoring()
        self.execution_time_monitoring.evolutionMonitoring()

    def clusteringHomogeneityMonitoring(self):
        if self.ilab:
            self.clustering_homogeneity_monitoring = ClusteringEvaluationMonitoring(self)
            self.clustering_homogeneity_monitoring.iterationMonitoring()
            self.clustering_homogeneity_monitoring.evolutionMonitoring()
