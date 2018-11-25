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

from .monitoring.Monitoring import Monitoring
from .strategies.queries.Query import NoAnnotationBudget
from .UpdateModel import UpdateModel
from SecuML.core.tools.core_exceptions import SecuMLcoreException


class NoAnnotationAdded(SecuMLcoreException):

    def __str__(self):
        return 'The iteration has not added any annotation.'


class NoUnlabeledDataLeft(SecuMLcoreException):

    def __str__(self):
        return 'There remains no unlabeled instances to be annotated.'


class Iteration(object):

    def __init__(self, conf, iteration_number, datasets=None,
                 prev_iter=None, budget=None):
        self.prev_iter = prev_iter
        self.conf = conf
        self.datasets = datasets
        self.budget = budget
        self.iteration_number = iteration_number

    def setQueryStrategy(self):
        strategy = self.conf.getStrategy(self)
        self.annotations = strategy

    def runIteration(self):
        self.checkUnlabeledData()
        self.setQueryStrategy()
        self.conf.logger.info('Start iteration n°%d' % self.iteration_number)
        start = time.time()
        self.initComputations()
        self.updateModel()
        self.generateQueries()
        self.answerAnnotationQueries()
        self.global_execution_time = time.time() - start
        self.conf.logger.info('End iteration n°%d' % self.iteration_number)
        self.conf.logger.info('Iteration n°%d: %f sec' % (self.iteration_number,
                                                    self.global_execution_time))
        return self.budget

    def checkUnlabeledData(self):
        unlabeled_data = self.datasets.getUnlabeledInstances()
        if unlabeled_data.numInstances() == 0:
            raise NoUnlabeledDataLeft()

    def generateQueries(self):
        self.annotations.generateQueries()

    def initComputations(self):
        if self.prev_iter is not None:
            self.prev_iter.finalComputations()
        self.monitoring = Monitoring(self)
        self.monitoring.generateStartMonitoring()

    def finalComputations(self):
        if not self.conf.auto:
            try:
                self.updateAnnotatedInstances()
            except (NoAnnotationBudget) as e:
                self.conf.logger.info(e)
                pass
        self.end_monitoring()
        self.checkAddedLabels()

    def end_monitoring(self):
        self.monitoring.generateEndMonitoring()

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

    # Raise the exception NoAnnotationAdded if no new annotation
    # has been added during the current iteration
    def checkAddedLabels(self):
        if not self.datasets.new_annotations:
            raise NoAnnotationAdded()
