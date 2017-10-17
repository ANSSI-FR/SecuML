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

from SecuML.ActiveLearning.Configuration import ActiveLearningConfFactory

from ActiveLearningExperiment import ActiveLearningExperiment
import ExperimentFactory
import experiment_db_tools

class RareCategoryDetectionExperiment(ActiveLearningExperiment):

    def __init__(self, project, dataset, session):
        ActiveLearningExperiment.__init__(self, project, dataset, session)
        self.kind = 'RareCategoryDetection'
        self.labeling_method = 'RareCategoryDetection'

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
        conf['__type__'] = 'RareCategoryDetection'
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
