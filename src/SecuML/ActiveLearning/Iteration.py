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

from SecuML.Tools import dir_tools

from Monitoring.Monitoring import Monitoring
from QueryStrategies.AnnotationQueries.AnnotationQuery import NoAnnotationBudget
from UpdateModel import UpdateModel

class NoLabelAdded(Exception):
    def __str__(self):
        return 'The iteration has not added any label.'

class Iteration(object):

    def __init__(self, conf, iteration_number,
                 datasets = None,
                 previous_iteration = None,
                 budget = None,
                 output_dir = None):
        self.previous_iteration = previous_iteration
        self.conf = conf
        self.datasets = datasets
        self.budget = budget
        self.iteration_number = iteration_number
        self.setOutputDirectory(output_dir)

    def setOutputDirectory(self, output_dir):
        self.al_dir = output_dir
        self.iteration_dir = None
        if self.al_dir is not None:
            self.iteration_dir  = self.al_dir
            self.iteration_dir += str(self.iteration_number) + '/'
            dir_tools.createDirectory(self.iteration_dir)

    def runIteration(self):
        print '\n\n%%%%%%%%%%%%%% Iteration ', self.iteration_number
        start = time.time()
        self.initializeMonitoring()
        self.updateModel()
        self.generateAnnotationQueries()
        self.answerAnnotationQueries()
        self.global_execution_time = time.time() - start
        print '\nEnd iteration ', self.global_execution_time
        return self.budget

    def generateAnnotationQueries(self):
        self.annotations = self.conf.getStrategy(self)
        self.annotations.generateAnnotationQueries()

    def initializeMonitoring(self):
        if self.previous_iteration is not None:
            self.previous_iteration.finalComputations()
        self.monitoring = Monitoring(self,
                                     self.conf.validation_conf is not None,
                                     self.al_dir, self.iteration_dir)
        self.monitoring.generateStartMonitoring()

    def finalComputations(self):
        if not self.conf.auto:
            try:
                self.updateLabeledInstances()
            except (NoAnnotationBudget) as e:
                print e
                pass
        self.monitoring.generateEndMonitoring()
        self.checkAddedLabels()

    def updateModel(self):
        self.update_model = UpdateModel(self)
        self.update_model.run()
        self.monitoring.generateModelPerformanceMonitoring()

    def answerAnnotationQueries(self):
        try:
            self.datasets.new_labels = False
            self.annotations.annotateAuto()
        except (NoAnnotationBudget) as e:
            print e
            pass

    ## Raise the exception NoLabelAdded if no new label
    ## was added during the current iteration
    def checkAddedLabels(self):
        if not self.datasets.new_labels:
            raise NoLabelAdded()
