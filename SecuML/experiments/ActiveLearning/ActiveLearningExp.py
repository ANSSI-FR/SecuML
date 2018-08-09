# SecuML
# Copyright (C) 2017-2018  ANSSI
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

from SecuML.core.ActiveLearning.ActiveLearning import ActiveLearning
from SecuML.core.ActiveLearning.Iteration import NoLabelAdded

from SecuML.experiments.ActiveLearning.IterationExp import IterationExp


class ActiveLearningExp(ActiveLearning):

    def __init__(self, experiment, datasets):
        ActiveLearning.__init__(self, experiment.conf, datasets)
        self.experiment = experiment

    def runIterations(self, output_dir=None):
        while True:
            try:
                self.runNextIteration(output_dir)
            except (NoLabelAdded) as e:
                self.experiment.conf.logger.info(e)
                break

    def runNextIteration(self, output_dir=None):
        self.current_iteration = IterationExp(self.experiment,
                                              self.iteration_number,
                                              datasets=self.datasets,
                                              previous_iteration=self.previous_iteration,
                                              budget=self.current_budget)
        self.current_budget = self.current_iteration.runIteration()
        self.iteration_number += 1
        self.current_iteration.previous_iteration = None
        self.previous_iteration = self.current_iteration

    def checkAnnotationQueriesAnswered(self):
        self.experiment.session.commit()
        return self.current_iteration.checkAnnotationQueriesAnswered()
