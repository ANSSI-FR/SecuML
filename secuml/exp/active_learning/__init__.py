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

import importlib
import pkgutil

from secuml.core.active_learning import ActiveLearning as CoreActiveLearning
from secuml.core.active_learning.iteration import NoAnnotationAdded
from secuml.core.active_learning.iteration import NoUnlabeledDataLeft
from secuml.exp import experiment
from secuml.exp.tools.db_tables import ActiveLearningExpAlchemy
from secuml.exp.experiment import Experiment

from .conf import ActiveLearningConf
from .conf import RcdConf
from .datasets import Datasets
from .iteration import Iteration
from . import strategies


for _, name, _ in pkgutil.iter_modules(strategies.__path__):
    class_name = ''.join(map(lambda x: x.capitalize(), name.split('_')))
    submodule = importlib.import_module(strategies.__name__ + '.' + name)
    strategies.get_factory().register(class_name, getattr(submodule,
                                                          class_name))


class ActiveLearningExp(Experiment):

    def add_to_db(self):
        Experiment.add_to_db(self)
        al_exp = ActiveLearningExpAlchemy(id=self.exp_id, current_iter=0,
                                          finished=False)
        self.session.add(al_exp)
        self.session.flush()

    def run(self):
        Experiment.run(self)
        datasets = Datasets(self.get_instances())
        active_learning = ActiveLearning(self, datasets)
        if not self.exp_conf.core_conf.auto:
            from secuml.exp.celery_app.app import secumlworker
            from secuml.exp.active_learning.celery_tasks import IterationTask
            options = {}
            # bind iterations object to IterationTask class
            active_learning.run_next_iter(output_dir=self.output_dir())
            IterationTask.iteration_object = active_learning
            # Start worker
            secumlworker.enable_config_fromcmdline = False
            secumlworker.run(**options)
        else:
            active_learning.run_iterations(output_dir=self.output_dir())

    def web_template(self):
        return 'active_learning/main.html'

    def get_current_iter(self):
        query = self.session.query(ActiveLearningExpAlchemy)
        query = query.filter(ActiveLearningExpAlchemy.id == self.exp_id)
        return query.one().current_iter


class ActiveLearning(CoreActiveLearning):

    def __init__(self, exp, datasets):
        CoreActiveLearning.__init__(self, exp.exp_conf.core_conf, datasets)
        self.exp = exp

    def run_iterations(self, output_dir=None):
        stop = False
        while not stop:
            stop = self.run_next_iter(output_dir)
        # Update the database. The active learning experiment is finished.
        query = self.exp.session.query(ActiveLearningExpAlchemy)
        query = query.filter(ActiveLearningExpAlchemy.id == self.exp.exp_id)
        exp_db = query.one()
        exp_db.finished = True

    def run_next_iter(self, output_dir=None):
        self.curr_iter = Iteration(self.exp, self.iter_num,
                                   datasets=self.datasets,
                                   prev_iter=self.prev_iter,
                                   budget=self.current_budget)
        try:
            self.current_budget = self.curr_iter.run()
        except (NoAnnotationAdded, NoUnlabeledDataLeft) as e:
            self.exp.exp_conf.logger.info(e)
            return True
        else:
            self.exp.session.commit()
            self.iter_num += 1
            self.curr_iter.prev_iter = None
            self.prev_iter = self.curr_iter
            return False


class RcdExp(ActiveLearningExp):
    pass


experiment.get_factory().register('ActiveLearning', ActiveLearningExp,
                                  ActiveLearningConf)


experiment.get_factory().register('Rcd', RcdExp, RcdConf)
