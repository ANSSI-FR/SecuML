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

from Experiment import Experiment
import ExperimentFactory
import experiment_db_tools

class ActiveLearningExperiment(Experiment):

    def __init__(self, project, dataset, session):
        Experiment.__init__(self, project, dataset, session)
        self.kind = 'ActiveLearning'
        self.labeling_method = None

    def setConfiguration(self, conf):
        self.conf = conf
        self.labeling_method = self.conf.labeling_method

    def generateSuffix(self):
        suffix = ''
        suffix += '__' + self.labeling_method
        suffix += self.conf.generateSuffix()
        return suffix

    def checkInputParams(self):
        self.conf.checkInputParams(self)

    @staticmethod
    def fromJson(obj, session):
        experiment = ActiveLearningExperiment(obj['project'], obj['dataset'], session)
        Experiment.expParamFromJson(experiment, obj)
        experiment.labeling_method  = obj['labeling_method']
        experiment.conf = ActiveLearningConfFactory.getFactory().fromJson(
                obj['conf'], experiment)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ActiveLearningExperiment'
        conf['labeling_method'] = self.labeling_method
        conf['conf'] = self.conf.toJson()
        return conf

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(description = 'Active Learning',
                formatter_class = argparse.RawTextHelpFormatter)
        Experiment.projectDatasetFeturesParser(parser)
        strategies = ['Ilab', 'RandomSampling', 'UncertaintySampling',
                      'CesaBianchi', 'Aladin', 'Gornitz']
        subparsers = parser.add_subparsers(dest = 'strategy')
        factory = ActiveLearningConfFactory.getFactory()
        for strategy in strategies:
            strategy_parser = subparsers.add_parser(strategy)
            factory.generateParser(strategy, strategy_parser)
        return parser

    def webTemplate(self):
        return 'ActiveLearning/active_learning.html'

    def getCurrentIteration(self):
        return experiment_db_tools.getCurrentIteration(self.session, self.experiment_id)

    def setExperimentFromArgs(self, args):
        self.setFeaturesFilenames(args.features_files)
        factory = ActiveLearningConfFactory.getFactory()
        active_learning_conf = factory.fromArgs(args.strategy, args, self)
        self.setConfiguration(active_learning_conf)
        self.checkInputParams()
        self.initLabels(args.init_labels_file)
        self.export()

ExperimentFactory.getFactory().registerClass('ActiveLearningExperiment',
                                             ActiveLearningExperiment)
