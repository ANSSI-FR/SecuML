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

## Package for float division (/)
## In order to perform integer division (//)
from __future__ import division
import time

from Datasets import Datasets
from Iteration import Iteration, NoLabelAdded

class Iterations(object):

    def __init__(self, experiment):
        self.experiment = experiment
        self.datasets = Datasets(experiment)
        self.budget = self.experiment.conf.budget
        self.iteration_number = 1
        self.current_budget = self.budget
        self.previous_iteration = None
        self.current_iteration = None

    def runIterations(self):
        while True:
            try:
                self.runNextIteration()
            except (NoLabelAdded) as e:
                print e
                break

    def runNextIteration(self):
        self.current_iteration = Iteration(self.experiment,
                                           self.iteration_number,
                                           datasets = self.datasets,
                                           previous_iteration = self.previous_iteration,
                                           budget = self.current_budget)
        self.current_budget = self.current_iteration.runIteration()
        self.iteration_number += 1
        self.current_iteration.previous_iteration = None
        self.previous_iteration = self.current_iteration

    def checkAnnotationQueriesAnswered(self):
        self.experiment.db.commit()
        return self.current_iteration.checkAnnotationQueriesAnswered()
