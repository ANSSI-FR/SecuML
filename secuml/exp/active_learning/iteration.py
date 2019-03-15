# SecuML
# Copyright (C) 2016-2019  ANSSI
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

import os
import os.path as path

from secuml.core.active_learning.iteration import Iteration as CoreIteration
from secuml.core.tools.color import display_in_green

from secuml.exp.tools.db_tables import ActiveLearningExpAlchemy

from . import strategies
from .monitoring.exec_times import ExecutionTimesMonitoring
from .update_model import UpdateModel


class Iteration(CoreIteration):

    def __init__(self, exp, iter_num, datasets=None, prev_iter=None,
                 budget=None):
        CoreIteration.__init__(self, exp.exp_conf.core_conf, iter_num,
                               datasets=datasets, prev_iter=prev_iter,
                               budget=budget)
        self.exp = exp
        self._set_output_dir()

    def _set_output_dir(self):
        self.al_dir = self.exp.output_dir()
        self.iteration_dir = path.join(self.al_dir, str(self.iter_num))

    def set_query_strategy(self):
        factory = strategies.get_factory()
        self.strategy = factory.get_strategy(self, self.conf.strategy_name)

    def init_computations(self):
        CoreIteration.init_computations(self)
        os.makedirs(self.iteration_dir)
        self.labels_monitoring.export(self.al_dir, self.iteration_dir)

    def end_monitoring(self):
        CoreIteration.end_monitoring(self)
        self.suggestions_accuracy.export(self.al_dir, self.iteration_dir)

    def update_model(self):
        self.update_model = UpdateModel(self)
        self.update_model.execute()
        self.update_model.monitoring(self.al_dir, self.iteration_dir)

    def generate_queries(self):
        # Update the iteration number in the DB.
        query = self.exp.session.query(ActiveLearningExpAlchemy)
        query = query.filter(ActiveLearningExpAlchemy.id == self.exp.exp_id)
        exp_db = query.one()
        exp_db.current_iter = self.iter_num
        #  Compute the annotation queries and export the monitoring.
        predictions = self.update_model.model_exp.get_predictions('test', None)
        CoreIteration.generate_queries(self, predictions)
        exp_db.annotations = True
        self._exec_times_monitoring()
        if not self.conf.auto:
            print(display_in_green(
                    '\nAnnotation queries for iteration %d have been '
                    'successfully computed. \n'
                    'Go to %s to answer the annotation queries. \n' %
                    (self.iter_num,
                     self.strategy.get_url())))

    def _exec_times_monitoring(self):
        self.exec_times_monitoring = ExecutionTimesMonitoring(self)
        self.exec_times_monitoring.export(self.al_dir, self.iteration_dir)

    def answer_queries(self):
        if self.conf.auto:
            CoreIteration.answer_queries(self)

    def update_annotated_instances(self):
        self.datasets.new_annotations = False
        # Update the datasets according to the new annotations
        self.datasets.check_annotations_with_db(self.exp)
        self.strategy.get_manual_annotations()
        self.datasets.check_new_annotations_with_db(self.exp)
        # Save the currently annotated instances
        self.save_annotations()

    def save_annotations(self):
        filename = 'annotations_exp%d_it%d.csv' % (self.exp.exp_conf.exp_id,
                                                   self.iter_num)
        dataset_conf = self.exp.exp_conf.dataset_conf
        secuml_conf = self.exp.exp_conf.secuml_conf
        filename = path.join(dataset_conf.input_dir(secuml_conf),
                             'annotations', filename)
        self.datasets.save_annotations(filename, self.exp)
