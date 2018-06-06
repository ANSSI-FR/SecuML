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

from SecuML.core.Classification.Configuration import ClassifierConfFactory
from SecuML.core.Classification.ClassifierDatasets import ClassifierDatasets
from SecuML.core.Classification.CvClassifierDatasets import CvClassifierDatasets
from SecuML.core.Configuration import Configuration

from SecuML.experiments import ExperimentFactory
from SecuML.experiments import db_tables
from SecuML.experiments.Classification.RunClassifier import RunClassifier
from SecuML.experiments.Data.Dataset import Dataset
from SecuML.experiments.Experiment import Experiment
from SecuML.experiments.InstancesFromExperiment import InstancesFromExperiment
from SecuML.experiments.ValidationExperiment import ValidationExperiment


class NoGroundTruth(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ClassificationExperiment(Experiment):

    def getKind(self):
        return 'Classification'

    def run(self):
        datasets = self.generateDatasets()
        classifier = self.conf.model_class(self.conf)
        run_classifier = RunClassifier(classifier, datasets, self)
        run_classifier.run()

    def createTestExperiment(self):
        test_dataset = self.conf.test_conf.test_dataset
        load_dataset = Dataset(self.project, test_dataset, self.session)
        if not load_dataset.isLoaded():
            load_dataset.load(self.logger)
        # Check if the validation experiments already exists
        test_exp = ValidationExperiment(self.project, test_dataset,
                                        self.session)
        test_exp.setConf(Configuration(self.conf.logger), self.features_filenames,
                         annotations_filename='ground_truth.csv')
        return test_exp

    def export(self):
        Experiment.export(self)
        if self.conf.test_conf.method == 'dataset':
            self.test_exp.export()
            with open(self.getOutputDirectory() + 'test_experiment.txt', 'w') as f:
                f.write(str(self.test_exp.experiment_id) + '\n')

    def generateDatasets(self):
        instances = InstancesFromExperiment(self).getInstances()
        test_instances = None
        if self.conf.test_conf.method == 'dataset':
            test_instances = InstancesFromExperiment(
                self.test_exp).getInstances()
        if self.conf.test_conf.method == 'cv':
            datasets = CvClassifierDatasets(self.conf.families_supervision,
                                            self.conf.num_folds,
                                            self.conf.sample_weight)
        else:
            datasets = ClassifierDatasets(self.conf.test_conf,
                                          self.conf.sample_weight)
        datasets.generateDatasets(instances, test_instances)
        return datasets

    def setConf(self, conf, features_files, annotations_filename=None,
                annotations_id=None):
        Experiment.setConf(self, conf, features_files,
                           annotations_filename=annotations_filename,
                           annotations_id=annotations_id)
        if self.conf.test_conf.method == 'dataset':
            self.test_exp = self.createTestExperiment()

    def _checkConf(self):
        return

    def generateSuffix(self):
        suffix = self.conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj, session):
        conf = ClassifierConfFactory.getFactory().fromJson(
            obj['classification_conf'])
        experiment = ClassificationExperiment(obj['project'], obj['dataset'],
                                              session, create=False)
        Experiment.expParamFromJson(experiment, obj, conf)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ClassificationExperiment'
        conf['classification_conf'] = self.conf.toJson()
        return conf

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(
            description='Learn a detection model. ' +
            'The ground-truth must be stored in annotations/ground_truth.csv.')
        Experiment.projectDatasetFeturesParser(parser)
        models = ['LogisticRegression', 'Svc', 'GaussianNaiveBayes',
                  'DecisionTree', 'RandomForest', 'GradientBoosting']
        subparsers = parser.add_subparsers(dest='model')
        factory = ClassifierConfFactory.getFactory()
        for model in models:
            model_parser = subparsers.add_parser(model)
            factory.generateParser(model, model_parser)
        return parser

    def webTemplate(self):
        return 'Classification/classification.html'

    def setExperimentFromArgs(self, args):
        factory = ClassifierConfFactory.getFactory()
        conf = factory.fromArgs(args.model, args, logger=self.logger)
        self.setConf(conf, args.features_files,
                     annotations_filename='ground_truth.csv')
        self.export()


ExperimentFactory.getFactory().registerClass('ClassificationExperiment',
                                             ClassificationExperiment)
