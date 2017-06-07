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

from SecuML.Tools import dir_tools
from SecuML.Tools import mysql_tools

from Monitoring.Monitoring import Monitoring
from QueryStrategies.AnnotationQueries.AnnotationQuery import NoAnnotationBudget
from TrainTestValidation import TrainTestValidation

class NoLabelAdded(Exception):
    def __str__(self):
        return 'The iteration has not added any label.'

class Iteration(object):

    def __init__(self, experiment, iteration_number,
                 datasets = None,
                 previous_iteration = None,
                 budget = None):
        self.previous_iteration = previous_iteration
        self.experiment = experiment
        self.datasets = datasets
        self.budget = budget
        self.setIterationNumber(iteration_number)
        self.setOutputDirectory()

    def setIterationNumber(self, iteration_number):
        self.iteration_number = iteration_number
        if self.iteration_number is None:
            previous_iter = self.experiment.getCurrentIteration()
            self.iteration_number = previous_iter + 1

    def setOutputDirectory(self):
        self.AL_directory = dir_tools.getExperimentOutputDirectory(
                self.experiment)
        self.output_directory  = self.AL_directory
        self.output_directory += str(self.iteration_number) + '/'

    def runIteration(self):
        self.initializeMonitoring()
        self.generateAnnotationQueries()
        self.answerAnnotationQueries()
        return self.budget

    def generateAnnotationQueries(self):
        print '\n\n%%%%%%%%%%%%%% Iteration ', self.iteration_number, self.budget
        self.trainTestValidation()
        self.createDbLine()
        self.annotations = self.experiment.conf.getStrategy(self)
        self.annotations.generateAnnotationQueries()
        self.updateDbLine()

    def initializeMonitoring(self):
        if self.previous_iteration is not None:
            self.previous_iteration.finalComputations()
        dir_tools.createDirectory(self.output_directory)
        self.monitoring = Monitoring(self.datasets, self.experiment,
                                     self,
                                     self.experiment.validation_conf is not None)
        self.monitoring.generateStartMonitoring()

    def answerAnnotationQueries(self):
        if self.experiment.conf.auto:
            try:
                self.annotateAuto()
            except (NoAnnotationBudget) as e:
                print e
                pass

    def finalComputations(self):
        if not self.experiment.conf.auto:
            try:
                self.updateLabeledInstances()
            except (NoAnnotationBudget) as e:
                print e
                pass
        self.monitoring.generateEndMonitoring()
        self.checkAddedLabels()

    def trainTestValidation(self):
        self.train_test_validation = TrainTestValidation(self)
        self.train_test_validation.run()
        self.monitoring.generateModelPerformanceMonitoring()

    def annotateAuto(self):
        self.datasets.new_labels = False
        self.annotations.annotateAuto()

    ## Raise the exception NoLabelAdded if no new label
    ## was added during the current iteration
    def checkAddedLabels(self):
        if not self.datasets.new_labels:
            raise NoLabelAdded()

    def updateLabeledInstances(self):
        self.datasets.new_labels = False
        # Update the datasets according to the new labels
        self.experiment.db.commit()
        self.datasets.checkLabelsWithDB(
                self.experiment.cursor,
                self.experiment.experiment_label_id)
        self.annotations.getManualAnnotations()
        # Save the current labelled instances
        self.datasets.saveLabeledInstances(self.iteration_number)

    def createDbLine(self):
        if self.iteration_number == 1:
            types = ['INT UNSIGNED', 'INT UNSIGNED', 'BIT(1)']
            values = [self.experiment.experiment_id, self.iteration_number, False]
            mysql_tools.insertRowIntoTable(self.experiment.cursor, 'InteractiveExperiments',
                    values, types)
        else:
            query  = 'UPDATE InteractiveExperiments '
            query += 'SET current_iter = ' + str(self.iteration_number) + ', '
            query += 'annotations = 0 '
            query += 'WHERE id = ' + str(self.experiment.experiment_id) + ';'
            self.experiment.cursor.execute(query)
        self.experiment.db.commit()

    def updateDbLine(self):
        query  = 'UPDATE InteractiveExperiments '
        query += 'SET annotations = 1 '
        query += 'WHERE id = ' + str(self.experiment.experiment_id) + ';'
        self.experiment.cursor.execute(query)
        self.experiment.db.commit()
