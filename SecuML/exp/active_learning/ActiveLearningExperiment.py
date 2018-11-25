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

from SecuML.exp.tools import db_tools
from SecuML.exp import ExperimentFactory
from SecuML.exp.db_tables import ActiveLearningExpAlchemy
from SecuML.exp.active_learning.ActiveLearningExp import ActiveLearningExp
from SecuML.exp.active_learning.DatasetsExp import DatasetsExp
from SecuML.exp.classification.ValidationExperiment import ValidationConf
from SecuML.exp.classification.ValidationExperiment import ValidationExperiment
from SecuML.exp.conf.AnnotationsConf import AnnotationsConf
from SecuML.exp.conf.DatasetConf import DatasetConf
from SecuML.exp.conf.FeaturesConf import FeaturesConf
from SecuML.exp.Experiment import Experiment
from .ActiveLearningConf import ActiveLearningConf


class ActiveLearningExperiment(Experiment):

    def create_exp(self):
        self.createTestExperiment()
        Experiment.create_exp(self)

    def add_to_db(self):
        Experiment.add_to_db(self)
        al_exp = ActiveLearningExpAlchemy(id=self.experiment_id, current_iter=0,
                                          finished=False)
        self.session.add(al_exp)
        self.session.flush()

    def createTestExperiment(self):
        self.test_exp = None
        test_conf = self.exp_conf.core_conf.validation_conf
        if test_conf is not None:
            logger = self.exp_conf.secuml_conf.logger
            annotations_conf = AnnotationsConf('ground_truth.csv', None, logger)
            dataset_conf = DatasetConf(self.exp_conf.dataset_conf.project,
                                       test_conf.test_dataset, logger)
            features_conf = FeaturesConf(
                    self.exp_conf.features_conf.input_features,
                    logger)
            validation_conf = ValidationConf(self.exp_conf.secuml_conf,
                                             dataset_conf,
                                             features_conf,
                                             annotations_conf,
                                             None)
            self.test_exp = ValidationExperiment(validation_conf,
                                                 session=self.session)
            self.test_exp.run()
            self.exp_conf.test_exp_conf = validation_conf

    def run(self):
        Experiment.run(self)
        datasets = self.generateDatasets()
        active_learning = ActiveLearningExp(self, datasets)
        if not self.exp_conf.core_conf.auto:
            from SecuML.exp.celery_app.app import secumlworker
            from SecuML.exp.active_learning.CeleryTasks \
                    import IterationTask
            options = {}
            # bind iterations object to IterationTask class
            active_learning.runNextIteration(output_dir=self.output_dir())
            IterationTask.iteration_object = active_learning
            # Start worker
            secumlworker.enable_config_fromcmdline = False
            secumlworker.run(**options)
        else:
            active_learning.runIterations(output_dir=self.output_dir())

    def generateDatasets(self):
        instances = self.getInstances()
        validation_instances = None
        if self.exp_conf.core_conf.validation_conf is not None:
            validation_instances = self.test_exp.getInstances()
        return DatasetsExp(instances, validation_instances)

    def webTemplate(self):
        return 'active_learning/main.html'

    def getCurrentIteration(self):
        return db_tools.getCurrentIteration(self.session,
                                            self.exp_conf.experiment_id)


ExperimentFactory.getFactory().register('ActiveLearning',
                                        ActiveLearningExperiment,
                                        ActiveLearningConf)
