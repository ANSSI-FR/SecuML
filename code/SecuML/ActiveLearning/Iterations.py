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

## Package for float division (/)
## In order to perform integer division (//)
from __future__ import division

import time

from Iteration import Iteration, NoLabelAdded

class Iterations(object):

    def __init__(self, experiment, datasets, budget, auto):
        self.experiment = experiment
        self.datasets = datasets
        self.budget = budget
        self.auto = auto
        self.iteration_number = 1
        self.has_true_labels = self.datasets.instances.hasTrueLabels()

    def runIterations(self):
        if not self.auto:
            #print 'Check Initial Labels'
            #raw_input('Press Enter ...')
            self.experiment.db.commit()
            self.datasets.checkLabelsWithDB(self.experiment.cursor,
                    self.experiment.experiment_label_id)
            self.datasets.saveLabeledInstances(0)
        budget = self.budget
        previous_iteration = None
        while True:
            try:
                start = time.time()
                iteration = Iteration(
                        previous_iteration,
                        self.experiment,
                        self.datasets,
                        self.has_true_labels,
                        budget,
                        self.auto,
                        iteration_number = self.iteration_number)
                budget = iteration.run()
                self.iteration_number += 1
                iteration.previous_iteration = None
                previous_iteration = iteration
                print '%%%%%%%%%%%%%%%%% Iteration ', time.time() - start
            except (NoLabelAdded) as e:
                print e
                break
