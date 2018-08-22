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

import argparse
import os.path as path

from SecuML.core.ActiveLearning.Configuration import ActiveLearningConfFactory
from SecuML.core.Configuration import Configuration

from SecuML.experiments import ExperimentFactory
from SecuML.experiments import experiment_db_tools
from SecuML.experiments.ActiveLearning.ActiveLearningExp import ActiveLearningExp
from SecuML.experiments.ActiveLearning.DatasetsExp import DatasetsExp
from SecuML.experiments.Data.Dataset import Dataset
from SecuML.experiments.Experiment import Experiment
from SecuML.experiments.InstancesFromExperiment import InstancesFromExperiment
from SecuML.experiments.ValidationExperiment import ValidationExperiment


class ActiveLearningExperiment(Experiment):

    def __init__(self, project, dataset, session, experiment_name=None,
                 logger=None, create=True):
        Experiment.__init__(self, project, dataset, session,
                            experiment_name=experiment_name,
                            logger=logger, create=create)
        # query_strategy: vraiment utile  ?
        self.query_strategy = None

    def getKind(self):
        return 'ActiveLearning'

    def run(self):
        datasets = self.generateDatasets()
        active_learning = ActiveLearningExp(self, datasets)
        if not self.conf.auto:
            from SecuML.experiments.CeleryApp.app import secumlworker
            from SecuML.experiments.ActiveLearning.CeleryTasks import IterationTask
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

    def createValidationExperiment(self):
        test_dataset = self.conf.validation_conf.test_dataset
        load_dataset = Dataset(self.project, test_dataset, self.session)
        if not load_dataset.isLoaded():
            load_dataset.load(self.logger)
        # Check if the validation experiments already exists
        test_exp = ValidationExperiment(self.project, test_dataset,
                                        self.session)
        test_exp.setConf(Configuration(self.conf.logger), self.features_filename,
                         annotations_filename='ground_truth.csv')
        return test_exp

    def export(self):
        Experiment.export(self)
        if self.conf.validation_conf is not None:
            self.test_exp.export()
            filename = path.join(self.getOutputDirectory(),
                                 'test_experiment.txt')
            with open(filename, 'w') as f:
                f.write(str(self.test_exp.experiment_id) + '\n')

    def generateDatasets(self):
        instances = InstancesFromExperiment(self).getInstances()
        validation_instances = None
        if self.conf.validation_conf is not None:
            validation_instances = InstancesFromExperiment(
                self.test_exp).getInstances()
        datasets = DatasetsExp(self.conf, instances, validation_instances)
        return datasets

    def setConf(self, conf, features_file, annotations_filename=None,
                annotations_id=None):
        self.query_strategy = conf.query_strategy
        Experiment.setConf(self, conf, features_file,
                           annotations_filename=annotations_filename,
                           annotations_id=annotations_id)
        if self.conf.validation_conf is not None:
            self.test_exp = self.createValidationExperiment()

    def generateSuffix(self):
        suffix = ''
        suffix += '__' + self.query_strategy
        suffix += self.conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj, session):
        experiment = ActiveLearningExperiment(obj['project'], obj['dataset'],
                                              session, create=False)
        conf = ActiveLearningConfFactory.getFactory().fromJson(obj['conf'])
        Experiment.expParamFromJson(experiment, obj, conf)
        experiment.query_strategy = obj['query_strategy']
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ActiveLearningExperiment'
        conf['query_strategy'] = self.query_strategy
        conf['conf'] = self.conf.toJson()
        return conf

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(description='Active Learning',
                                         formatter_class=argparse.RawTextHelpFormatter)
        Experiment.projectDatasetFeturesParser(parser)
        strategies = ['Ilab', 'RandomSampling', 'UncertaintySampling',
                      'CesaBianchi', 'Aladin', 'Gornitz']
        subparsers = parser.add_subparsers(dest='strategy')
        factory = ActiveLearningConfFactory.getFactory()
        for strategy in strategies:
            strategy_parser = subparsers.add_parser(strategy)
            factory.generateParser(strategy, strategy_parser)
        return parser

    def webTemplate(self):
        return 'ActiveLearning/active_learning.html'

    def getCurrentIteration(self):
        return experiment_db_tools.getCurrentIteration(self.session,
                                                       self.experiment_id)

    def setExperimentFromArgs(self, args):
        factory = ActiveLearningConfFactory.getFactory()
        conf = factory.fromArgs(args.strategy, args, logger=self.logger)
        self.setConf(conf, args.features_file,
                     annotations_filename=args.init_annotations_file)
        self.export()


ExperimentFactory.getFactory().registerClass('ActiveLearningExperiment',
                                             ActiveLearningExperiment)
