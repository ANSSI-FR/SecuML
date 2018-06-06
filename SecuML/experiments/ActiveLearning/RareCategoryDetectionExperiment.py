# SecuML
# Copyright (C) 2016-2017  ANSSI
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

import argparse

from SecuML.core.ActiveLearning.Configuration import ActiveLearningConfFactory

from SecuML.experiments import experiment_db_tools
from SecuML.experiments import ExperimentFactory
from SecuML.experiments.ActiveLearning.ActiveLearningExp import ActiveLearningExp
from SecuML.experiments.ActiveLearning.ActiveLearningExperiment import ActiveLearningExperiment


class RareCategoryDetectionExperiment(ActiveLearningExperiment):

    def __init__(self, project, dataset, session, experiment_name=None,
                 logger=None, create=True):
        ActiveLearningExperiment.__init__(self, project, dataset, session,
                                          experiment_name=experiment_name,
                                          logger=logger, create=create)
        # query_strategy: vraiment utile  ?
        self.query_strategy = 'RareCategoryDetection'

    def getKind(self):
        return 'RareCategoryDetection'

    def run(self):
        datasets = self.generateDatasets()
        active_learning = ActiveLearningExp(self, datasets)
        if not self.conf.auto:
            from SecuML.CeleryApp.app import secumlworker
            from SecuML.CeleryApp.activeLearningTasks import IterationTask
            options = {}
            # bind iterations object to IterationTask class
            active_learning.runNextIteration(
                output_dir=self.getOutputDirectory())
            IterationTask.iteration_object = active_learning
            # Start worker
            secumlworker.enable_config_fromcmdline = False
            secumlworker.run(**options)
        else:
            active_learning.runIterations(output_dir=self.getOutputDirectory())

    @staticmethod
    def fromJson(obj, session):
        experiment = RareCategoryDetectionExperiment(obj['project'], obj['dataset'],
                                                     session, create=False)
        conf = ActiveLearningConfFactory.getFactory().fromJson(obj['conf'])
        ActiveLearningExperiment.expParamFromJson(experiment, obj, conf)
        experiment.query_strategy = obj['query_strategy']
        return experiment

    def toJson(self):
        conf = ActiveLearningExperiment.toJson(self)
        conf['__type__'] = 'RareCategoryDetectionExperiment'
        conf['query_strategy'] = self.query_strategy
        conf['conf'] = self.conf.toJson()
        return conf

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(description='Rare Category Detection',
                                         formatter_class=argparse.RawTextHelpFormatter)
        ActiveLearningExperiment.projectDatasetFeturesParser(parser)
        factory = ActiveLearningConfFactory.getFactory()
        factory.generateParser('RareCategoryDetection', parser)
        return parser

    def webTemplate(self):
        return 'ActiveLearning/active_learning.html'

    def getCurrentIteration(self):
        return experiment_db_tools.getCurrentIteration(self.session, self.experiment_id)

    def setExperimentFromArgs(self, args):
        factory = ActiveLearningConfFactory.getFactory()
        conf = factory.fromArgs('RareCategoryDetection',
                                args, logger=self.logger)
        self.setConf(conf, args.features_files,
                     annotations_filename=args.init_annotations_file)
        self.export()


ExperimentFactory.getFactory().registerClass('RareCategoryDetectionExperiment',
                                             RareCategoryDetectionExperiment)
