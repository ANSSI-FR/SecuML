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

from SecuML.core.active_learning.ActiveLearning import ActiveLearning
from SecuML.core.active_learning.Iteration import NoAnnotationAdded
from SecuML.core.active_learning.Iteration import NoUnlabeledDataLeft

from SecuML.exp.active_learning.IterationExp import IterationExp
from SecuML.exp.db_tables import ActiveLearningExpAlchemy


class ActiveLearningExp(ActiveLearning):

    def __init__(self, experiment, datasets):
        ActiveLearning.__init__(self, experiment.exp_conf.core_conf, datasets)
        self.experiment = experiment

    def runIterations(self, output_dir=None):
        stop = False
        while not stop:
            stop = self.runNextIteration(output_dir)
        # Update the database. The active learning experiment is finished.
        query = self.experiment.session.query(ActiveLearningExpAlchemy)
        query = query.filter(
                ActiveLearningExpAlchemy.id == self.experiment.experiment_id)
        exp_db = query.one()
        exp_db.finished = True

    def runNextIteration(self, output_dir=None):
        self.curr_iter = IterationExp(self.experiment,
                                      self.iteration_number,
                                      datasets=self.datasets,
                                      prev_iter=self.prev_iter,
                                      budget=self.current_budget)
        try:
            self.current_budget = self.curr_iter.runIteration()
        except (NoAnnotationAdded, NoUnlabeledDataLeft) as e:
            self.experiment.exp_conf.logger.info(e)
            return True
        else:
            self.experiment.session.commit()
            self.iteration_number += 1
            self.curr_iter.prev_iter = None
            self.prev_iter = self.curr_iter
            return False
