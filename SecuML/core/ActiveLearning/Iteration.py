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

import time

from .Monitoring.Monitoring import Monitoring
from .QueryStrategies.AnnotationQueries.AnnotationQuery import NoAnnotationBudget
from .UpdateModel import UpdateModel


class NoLabelAdded(Exception):

    def __str__(self):
        return 'The iteration has not added any label.'


class Iteration(object):

    def __init__(self, conf, iteration_number,
                 datasets=None,
                 previous_iteration=None,
                 budget=None):
        self.previous_iteration = previous_iteration
        self.conf = conf
        self.datasets = datasets
        self.budget = budget
        self.iteration_number = iteration_number

    def setQueryStrategy(self):
        strategy = self.conf.getStrategy(self)
        self.annotations = strategy

    def runIteration(self):
        self.setQueryStrategy()
        self.conf.logger.info('Start iteration n°' +
                              str(self.iteration_number))
        start = time.time()
        self.initComputations()
        self.updateModel()
        self.generateAnnotationQueries()
        self.answerAnnotationQueries()
        self.global_execution_time = time.time() - start
        self.conf.logger.info('End iteration n°' + str(self.iteration_number))
        self.conf.logger.info('Iteration n°' + str(self.iteration_number) +
                              ': ' + str(self.global_execution_time) + ' sec')
        return self.budget

    def generateAnnotationQueries(self):
        self.annotations.generateAnnotationQueries()

    def initComputations(self):
        if self.previous_iteration is not None:
            self.previous_iteration.finalComputations()
        self.monitoring = Monitoring(self)
        self.monitoring.generateStartMonitoring()

    def finalComputations(self):
        if not self.conf.auto:
            try:
                self.updateAnnotatedInstances()
            except (NoAnnotationBudget) as e:
                self.conf.logger.info(e)
                pass
        self.monitoring.generateEndMonitoring()
        self.checkAddedLabels()

    def updateModel(self):
        self.update_model = UpdateModel(self)
        self.update_model.run()
        self.monitoring.generateModelPerformanceMonitoring()

    def answerAnnotationQueries(self):
        try:
            self.datasets.new_annotations = False
            self.annotations.annotateAuto()
        except (NoAnnotationBudget) as e:
            self.conf.logger.info(e)
            pass

    # Raise the exception NoLabelAdded if no new label
    # has been added during the current iteration
    def checkAddedLabels(self):
        if not self.datasets.new_annotations:
            raise NoLabelAdded()
