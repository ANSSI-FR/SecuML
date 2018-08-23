# SecuML
# Copyright (C) 2017  ANSSI
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

from SecuML.core.ActiveLearning.Iteration import Iteration
from SecuML.core.ActiveLearning.QueryStrategies.AnnotationQueries.AnnotationQuery \
        import NoAnnotationBudget
from SecuML.core.Tools import colors_tools
from SecuML.core.Tools import dir_tools

from SecuML.experiments.ActiveLearning.QueryStrategies \
        import ActiveLearningStrategyFactoryExp

from SecuML.experiments.ActiveLearning.UpdateModelExp import UpdateModelExp
from SecuML.experiments.db_tables import ExperimentsAlchemy
from SecuML.experiments.Tools import dir_exp_tools


class IterationExp(Iteration):

    def __init__(self, experiment, iteration_number,
                 datasets=None,
                 previous_iteration=None,
                 budget=None):
        Iteration.__init__(self, experiment.conf, iteration_number,
                           datasets=datasets,
                           previous_iteration=previous_iteration,
                           budget=budget)
        self.experiment = experiment
        self.setOutputDirectory()

    def setOutputDirectory(self):
        self.al_dir = self.experiment.getOutputDirectory()
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

    def finalComputations(self):
        if not self.conf.auto:
            try:
                self.updateAnnotatedInstances()
            except (NoAnnotationBudget) as e:
                self.conf.logger.info(e)
                pass
        self.monitoring.generateEndMonitoring()
        self.monitoring.exportEndMonitoring(self.al_dir, self.iteration_dir)
        self.checkAddedLabels()

    def updateModel(self):
        self.update_model = UpdateModelExp(self)
        self.update_model.run()
        self.monitoring.generateModelPerformanceMonitoring()
        self.monitoring.exportModelPerformanceMonitoring(
            self.al_dir, self.iteration_dir)

    def generateAnnotationQueries(self):
        query = self.experiment.session.query(ExperimentsAlchemy)
        query = query.filter(ExperimentsAlchemy.id ==
                             self.experiment.experiment_id)
        exp_db = query.one()
        exp_db.current_iter = self.iteration_number
        self.annotations.generateAnnotationQueries()
        exp_db.annotations = True
        self.monitoring.exportExecutionTimeMonitoring(
            self.al_dir, self.iteration_dir)
        if not self.conf.auto:
            print(colors_tools.displayInGreen(
                    '\nAnnotation queries for iteration %d have been successfully '
                    'computed. \n'
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
        # Save the currently annotated instances
        self.saveAnnotatedInstances()

    def saveAnnotatedInstances(self):
        filename = 'annotations_%s_exp%d_it%d.csv' % (
                self.experiment.query_strategy,
                self.experiment.experiment_id,
                self.iteration_number)
        filename = path.join(dir_exp_tools.getDatasetDirectory(
                                    self.experiment.secuml_conf,
                                    self.experiment.project,
                                    self.experiment.dataset),
                             'annotations',
                             filename)
        self.datasets.saveAnnotatedInstances(filename, self.experiment)

    def checkAnnotationQueriesAnswered(self):
        return self.annotations.checkAnnotationQueriesAnswered()
