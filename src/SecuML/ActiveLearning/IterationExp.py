## SecuML
## Copyright (C) 2017  ANSSI
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

from SecuML.db_tables import ExperimentsAlchemy
from SecuML.Tools import dir_tools

from UpdateModelExp import UpdateModelExp
from Iteration import Iteration

class IterationExp(Iteration):

    def __init__(self, experiment, iteration_number,
                 datasets = None,
                 previous_iteration = None,
                 budget = None):
        Iteration.__init__(self, experiment.conf, iteration_number,
                datasets = datasets,
                previous_iteration = previous_iteration,
                budget = budget,
                output_dir = experiment.getOutputDirectory())
        self.experiment = experiment

    def updateModel(self):
        self.update_model = UpdateModelExp(self)
        self.update_model.run()
        self.monitoring.generateModelPerformanceMonitoring()

    def generateAnnotationQueries(self):
        query = self.experiment.session.query(ExperimentsAlchemy)
        query = query.filter(ExperimentsAlchemy.id == self.experiment.experiment_id)
        exp_db = query.one()
        exp_db.current_iter = self.iteration_number
        self.experiment.session.commit()

        self.annotations = self.conf.getStrategyExp(self)
        self.annotations.generateAnnotationQueries()

        exp_db.annotations = True
        self.experiment.session.commit()

    def answerAnnotationQueries(self):
        if self.conf.auto:
            Iteration.answerAnnotationQueries(self)

    def updateLabeledInstances(self):
        self.datasets.new_labels = False
        # Update the datasets according to the new labels
        self.experiment.session.commit()
        self.datasets.checkLabelsWithDB(self.experiment)
        self.annotations.getManualAnnotations()
        # Save the currently annotated instances
        self.saveLabeledInstances()

    def saveLabeledInstances(self):
        for i in ['annotations', 'labels']:
            filename  = dir_tools.getDatasetDirectory(
                    self.experiment.project,
                    self.experiment.dataset)
            filename += 'labels/' + i + '_'
            filename += self.experiment.labeling_method + '_'
            filename += 'exp' + str(self.experiment.experiment_id) + '_'
            filename += 'it' + str(self.iteration_number) + '.csv'
            self.datasets.saveLabeledInstances(i, filename)

    def checkAnnotationQueriesAnswered(self):
        return self.annotations.checkAnnotationQueriesAnswered()
