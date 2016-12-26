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

from SecuML.Data.Dataset import Dataset
from SecuML.Data import labels_tools
from SecuML.Tools import dir_tools

from TrainTestValidation import TrainTestValidation
from CheckPredictedLabels import CheckPredictedLabels, NoAnnotationBudget

from Monitoring.Monitoring import Monitoring

from QueryStrategies.CesaBianchi import CesaBianchi
from QueryStrategies.ClosestToBoundary import ClosestToBoundary
from QueryStrategies.ILAB import ILAB
from QueryStrategies.RandomSampling import RandomSampling

class NoLabelAdded(Exception):
    def __str__(self):
        return 'The iteration has not added any label.'

class Iteration(object):

    def __init__(self, previous_iteration, experiment, datasets, has_true_labels, 
            budget, auto, iteration_number = None):
        self.previous_iteration = previous_iteration
        self.experiment = experiment
        self.datasets = datasets
        self.has_true_labels = has_true_labels
        self.auto = auto
        self.budget = budget
        self.setIterationNumber(iteration_number)
        self.setOutputDirectory()

    def setIterationNumber(self, iteration_number):
        self.iteration_number = iteration_number
        if self.iteration_number is None:
            self.iteration_number = labels_tools.getIterationNumber(
                    self.experiment.cursor,
                    self.experiment.experiment_label_id) + 1
    
    def setOutputDirectory(self):
        self.AL_directory = dir_tools.getExperimentOutputDirectory(
                self.experiment)
        self.output_directory  = self.AL_directory
        self.output_directory += str(self.iteration_number) + '/'

    def run(self):
        print '\n\n%%%%%%%%%%%%%% Iteration ', self.iteration_number, self.budget
        dir_tools.createDirectory(self.output_directory)
        self.trainTestValidation()
        self.generateMonitoring()
        self.generateAnnotationQueries()
        self.executionTimeMonitoring()
        if self.auto:
            try:
                self.annotateAuto()
            except (NoAnnotationBudget) as e:
                print e
                pass
            self.clusteringHomogeneityMonitoring()
            self.checkAddedLabels()
        else:
            print 'Annotations ...'
            raw_input('Press Enter ...')
            try:
                self.updateLabeledInstances()
            except (NoAnnotationBudget) as e:
                print e
                pass
            self.checkAddedLabels()
        return self.budget

    ################
    ## Monitoring ##
    ################

    def generateMonitoring(self):
        self.monitoring = Monitoring(self.datasets, self.experiment,
                self,
                self.experiment.validation_conf is not None)
        self.monitoring.iterationMonitoring()
        self.monitoring.evolutionMonitoring()

    def executionTimeMonitoring(self):
        self.monitoring.generateExecutionTimeMonitoring()

    def clusteringHomogeneityMonitoring(self):
        self.monitoring.clusteringHomogeneityMonitoring()

    #####################
    ## Active Learning ##
    #####################

    def trainTestValidation(self):
        self.train_test_validation = TrainTestValidation(self)
        self.train_test_validation.run()

    def generateAnnotationQueries(self):
        labeling_method = self.experiment.labeling_method
        if labeling_method == 'random_sampling':
            self.annotations = RandomSampling(self)
        if labeling_method == 'closest_to_boundary':
            self.annotations = ClosestToBoundary(self)
        if labeling_method == 'ILAB':
            self.annotations = ILAB(self)
        if labeling_method == 'Cesa_Bianchi':
            self.annotations = CesaBianchi(self)
        self.annotations.generateAnnotationQueries()

    def annotateAuto(self):
        self.datasets.new_labels = False
        self.annotations.annotateAuto()

    ## If the instance is in PredictedLabels (for the given experiment)
    ## then PredictedLabels.final_label is set to "label"
    ## Then, the new label is added to Label
    ## If there is already a label for "instance_id" in "experiment"
    ## nothing is done.
    def addLabel(self, instance_id, label, sublabel, method):
        labels_checking = CheckPredictedLabels(self)
        labels_checking.addLabel(instance_id, label,
                sublabel, method)

    def updateLabeledInstances(self):
        self.datasets.new_labels = False
        labels_checking = CheckPredictedLabels(self)
        labels_checking.checkPredictedLabelsDB()
        self.datasets.saveLabeledInstances(self.iteration_number)

    ## Raise the exception NoLabelAdded if no new label
    ## was added during the current iteration
    def checkAddedLabels(self):
        if not self.datasets.new_labels:
            raise NoLabelAdded()
