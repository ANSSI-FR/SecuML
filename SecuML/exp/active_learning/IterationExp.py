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

import os.path as path

from SecuML.core.active_learning.Iteration import Iteration
from SecuML.core.tools import colors_tools
from SecuML.core.tools import dir_tools

from SecuML.exp.active_learning.strategies \
        import ActiveLearningStrategyFactoryExp

from SecuML.exp.active_learning.UpdateModelExp import UpdateModelExp
from SecuML.exp.db_tables import ActiveLearningExpAlchemy


class IterationExp(Iteration):

    def __init__(self, experiment, iteration_number, datasets=None,
                 prev_iter=None, budget=None):
        Iteration.__init__(self, experiment.exp_conf.core_conf,
                           iteration_number, datasets=datasets,
                           prev_iter=prev_iter, budget=budget)
        self.experiment = experiment
        self._set_output_dir()

    def _set_output_dir(self):
        self.al_dir = self.experiment.output_dir()
        self.iteration_dir = path.join(self.al_dir,
                                       str(self.iteration_number))

    def setQueryStrategy(self):
        factory = ActiveLearningStrategyFactoryExp.getFactory()
        strategy = factory.getStrategy(self, self.conf.query_strategy)
        self.annotations = strategy

    def initComputations(self):
        Iteration.initComputations(self)
        dir_tools.createDirectory(self.iteration_dir)
        self.monitoring.exportStartMonitoring(self.al_dir, self.iteration_dir)

    def end_monitoring(self):
        self.monitoring.generateEndMonitoring()
        self.monitoring.exportEndMonitoring(self.al_dir, self.iteration_dir)

    def updateModel(self):
        self.update_model = UpdateModelExp(self)
        self.update_model.run()
        self.monitoring.generateModelPerformanceMonitoring()
        self.monitoring.exportModelPerformanceMonitoring(self.al_dir,
                                                         self.iteration_dir)

    def generateQueries(self):
        # Update the iteration number in the DB.
        query = self.experiment.session.query(ActiveLearningExpAlchemy)
        query = query.filter(
                ActiveLearningExpAlchemy.id == self.experiment.experiment_id)
        exp_db = query.one()
        exp_db.current_iter = self.iteration_number
        #  Compute the annotation queries and export the monitoring.
        self.annotations.generateQueries()
        exp_db.annotations = True
        self.monitoring.exportExecutionTimeMonitoring(self.al_dir,
                                                      self.iteration_dir)
        if not self.conf.auto:
            print(colors_tools.display_in_green(
                    '\nAnnotation queries for iteration %d have been '
                    'successfully computed. \n'
                    'Go to %s to answer the annotation queries. \n' %
                    (self.iteration_number,
                     self.annotations.getUrl())))

    def answerAnnotationQueries(self):
        if self.conf.auto:
            Iteration.answerAnnotationQueries(self)

    def updateAnnotatedInstances(self):
        self.datasets.new_annotations = False
        # Update the datasets according to the new annotations
        self.datasets.checkAnnotationsWithDB(self.experiment)
        self.annotations.getManualAnnotations()
        self.datasets.checkNewAnnotationsWithDB(self.experiment)
        # Save the currently annotated instances
        self.saveAnnotatedInstances()

    def saveAnnotatedInstances(self):
        filename = 'annotations_exp%d_it%d.csv' % (
                self.experiment.exp_conf.experiment_id,
                self.iteration_number)
        dataset_conf = self.experiment.exp_conf.dataset_conf
        secuml_conf = self.experiment.exp_conf.secuml_conf
        filename = path.join(dataset_conf.input_dir(secuml_conf), 'annotations',
                             filename)
        self.datasets.saveAnnotatedInstances(filename, self.experiment)
