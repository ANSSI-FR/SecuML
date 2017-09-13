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

import time

from SecuML.db_tables import ExperimentsAlchemy
from SecuML.Tools import dir_tools

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
        self.AL_directory = self.experiment.getOutputDirectory()
        self.output_directory  = self.AL_directory
        self.output_directory += str(self.iteration_number) + '/'

    def runIteration(self):
        print '\n\n%%%%%%%%%%%%%% Iteration ', self.iteration_number
        start = time.time()
        self.initializeMonitoring()
        self.generateAnnotationQueries()
        self.answerAnnotationQueries()
        self.global_execution_time = time.time() - start
        print '\nEnd iteration ', self.global_execution_time
        return self.budget

    def generateAnnotationQueries(self):
        query = self.experiment.session.query(ExperimentsAlchemy)
        query = query.filter(ExperimentsAlchemy.id == self.experiment.experiment_id)
        exp_db = query.one()
        self.trainTestValidation()
        exp_db.current_iter = self.iteration_number
        self.experiment.session.commit()
        self.annotations = self.experiment.conf.getStrategy(self)
        self.annotations.generateAnnotationQueries()
        exp_db.annotations = True
        self.experiment.session.commit()

    def initializeMonitoring(self):
        if self.previous_iteration is not None:
            self.previous_iteration.finalComputations()
        dir_tools.createDirectory(self.output_directory)
        self.monitoring = Monitoring(self.datasets, self.experiment,
                                     self,
                                     self.experiment.conf.validation_conf is not None)
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
        self.experiment.session.commit()
        self.datasets.checkLabelsWithDB(self.experiment)
        self.annotations.getManualAnnotations()
        # Save the current labelled instances
        self.datasets.saveLabeledInstances(self.iteration_number)

    def checkAnnotationQueriesAnswered(self):
        return self.annotations.checkAnnotationQueriesAnswered()
