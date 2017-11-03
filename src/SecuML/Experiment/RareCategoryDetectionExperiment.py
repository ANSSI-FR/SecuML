## SecuML
## Copyright (C) 2016-2017  ANSSI
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

import argparse

from SecuML.ActiveLearning.ActiveLearningExp import ActiveLearningExp
from SecuML.ActiveLearning.Configuration import ActiveLearningConfFactory

import ExperimentFactory
from ActiveLearningExperiment import ActiveLearningExperiment

import experiment_db_tools

class RareCategoryDetectionExperiment(ActiveLearningExperiment):

    def __init__(self, project, dataset, session, experiment_name = None):
        ActiveLearningExperiment.__init__(self, project, dataset, session,
                                          experiment_name = experiment_name)
        self.kind = 'RareCategoryDetection'
        self.labeling_method = 'RareCategoryDetection'

    def run(self):
        datasets = self.generateDatasets()
        active_learning = ActiveLearningExp(self ,datasets)
        if not self.conf.auto:
            from CeleryApp.app import secumlworker
            from CeleryApp.activeLearningTasks import IterationTask
            options = {}
            # bind iterations object to IterationTask class
            active_learning.runNextIteration(output_dir = self.getOutputDirectory())
            IterationTask.iteration_object = active_learning
            # Start worker
            secumlworker.enable_config_fromcmdline = False
            secumlworker.run(**options)
        else:
            active_learning.runIterations(output_dir = self.getOutputDirectory())

    @staticmethod
    def fromJson(obj, session):
        experiment = RareCategoryDetectionExperiment(obj['project'], obj['dataset'],
                                                     session)
        ActiveLearningExperiment.expParamFromJson(experiment, obj)
        experiment.labeling_method  = obj['labeling_method']
        experiment.conf = ActiveLearningConfFactory.getFactory().fromJson(
                obj['conf'], experiment)
        return experiment

    def toJson(self):
        conf = ActiveLearningExperiment.toJson(self)
        conf['__type__'] = 'RareCategoryDetectionExperiment'
        conf['labeling_method'] = self.labeling_method
        conf['conf'] = self.conf.toJson()
        return conf

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(description = 'Rare Category Detection',
                formatter_class = argparse.RawTextHelpFormatter)
        ActiveLearningExperiment.projectDatasetFeturesParser(parser)
        factory = ActiveLearningConfFactory.getFactory()
        factory.generateParser('RareCategoryDetection', parser)
        return parser

    def webTemplate(self):
        return 'ActiveLearning/active_learning.html'

    def getCurrentIteration(self):
        return experiment_db_tools.getCurrentIteration(self.session, self.experiment_id)

    def setExperimentFromArgs(self, args):
        self.setFeaturesFilenames(args.features_files)
        factory = ActiveLearningConfFactory.getFactory()
        active_learning_conf = factory.fromArgs('RareCategoryDetection', args, self)
        self.setConfiguration(active_learning_conf)
        self.initLabels(args.init_labels_file)
        self.export()

ExperimentFactory.getFactory().registerClass('RareCategoryDetectionExperiment',
                                             RareCategoryDetectionExperiment)
