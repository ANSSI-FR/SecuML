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
import json
import os.path as path

from SecuML.core.Classification.Configuration import ClassifierConfFactory
from SecuML.core.Classification.Configuration.AlertsConfiguration \
        import AlertsConfiguration
from SecuML.core.Classification.Configuration.TestConfiguration.ValidationDatasetConf \
        import ValidationDatasetConf
from SecuML.core.Clustering.Configuration import ClusteringConfFactory
from SecuML.core.Configuration import Configuration

from SecuML.experiments import ExperimentFactory
from SecuML.experiments import db_tables
from SecuML.experiments.Classification.RunClassifier import RunClassifier
from SecuML.experiments.Data.InstancesFromExperiment \
        import InstancesFromExperiment
from SecuML.experiments.Experiment import Experiment
from SecuML.experiments.Tools import dir_exp_tools
from SecuML.experiments.Tools.exp_exceptions import SecuMLexpException
from SecuML.experiments.ValidationExperiment import ValidationExperiment


class NoGroundTruth(SecuMLexpException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ExperimentNotFound(SecuMLexpException):

    def __init__(self, experiment_id):
        self.experiment_id = experiment_id

    def __str__(self):
        return('The experiment %d cannot be found.'
               % (self.experiment_id))


class InvalidModelExperimentKind(SecuMLexpException):

    def __init__(self, experiment_kind):
        self.experiment_kind = experiment_kind

    def __str__(self):
        return('model-exp-id is a %s experiment '
               'while it must be a DIADEM or an ActiveLearning experiment.'
               % (self.experiment_kind))


class ClassificationExperiment(Experiment):

    def __init__(self, secuml_conf, session=None):
        Experiment.__init__(self, secuml_conf, session=session)
        self.already_trained = None

    def getKind(self):
        return 'Classification'

    def run(self):
        datasets = self.generateDatasets()
        classifier = self.conf.model_class(self.conf)
        run_classifier = RunClassifier(classifier, datasets, self)
        run_classifier.run()

    def createTestExperiment(self):
        test_dataset = self.conf.test_conf.test_dataset
        test_exp = ValidationExperiment(self.secuml_conf,
                                        session=self.session)
        test_exp.initExperiment(self.project, test_dataset)
        test_exp.setConf(Configuration(self.conf.logger),
                         self.features_filename,
                         annotations_filename='ground_truth.csv')
        return test_exp

    def export(self):
        Experiment.export(self)
        if self.conf.test_conf.method == 'dataset':
            self.test_exp.export()
            filename = path.join(self.getOutputDirectory(),
                                 'test_experiment.txt')
            with open(filename, 'w') as f:
                f.write(str(self.test_exp.experiment_id) + '\n')

    def generateDatasets(self):
        instances = InstancesFromExperiment(self).getInstances()
        test_instances = None
        if self.conf.test_conf.method == 'dataset':
            instances_exp = InstancesFromExperiment(self.test_exp)
            test_instances = instances_exp.getInstances()
        datasets = self.conf.test_conf.generateDatasets(self.conf,
                                                        instances,
                                                        test_instances)
        return datasets

    def setConf(self, conf, features_file, annotations_filename=None,
                annotations_id=None):
        Experiment.setConf(self, conf, features_file,
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
    def fromJson(obj, secuml_conf):
        conf = ClassifierConfFactory.getFactory().fromJson(
            obj['classification_conf'])
        experiment = ClassificationExperiment(secuml_conf)
        experiment.initExperiment(obj['project'], obj['dataset'],
                                  create=False)
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
            description='Learn a detection model. '
                        'The ground-truth must be stored in '
                        'annotations/ground_truth.csv.')
        Experiment.projectDatasetFeturesParser(parser)
        models = ['LogisticRegression', 'Svc', 'GaussianNaiveBayes',
                  'DecisionTree', 'RandomForest', 'GradientBoosting']
        subparsers = parser.add_subparsers(dest='model')
        subparsers.required = True
        factory = ClassifierConfFactory.getFactory()
        for model in models:
            model_parser = subparsers.add_parser(model)
            factory.generateParser(model, model_parser)
        ## Add subparser for already trained model
        already_trained = subparsers.add_parser('AlreadyTrained')
        factory.generateParser('AlreadyTrained', already_trained)
        return parser

    def webTemplate(self):
        return 'Classification/classification.html'

    def checkAlreadyTrainedConf(self, args):
        model_exp = db_tables.checkExperimentId(self.session, args.model_exp_id)
        # Check whether the experiment exists
        if model_exp is None:
            raise ExperimentNotFound(args.model_exp_id)
        # Check the type of the experiment
        if model_exp.kind not in ['Classification', 'ActiveLearning']:
            raise InvalidModelExperimentKind(model_exp.kind)
        ## only OneFoldTestConfiguration
        conf_filename = dir_exp_tools.getExperimentConfigurationFilename(
                self.secuml_conf,
                args.project,
                args.dataset,
                args.model_exp_id)
        return conf_filename

    def generateAlreadyTrainedConf(self, factory, args, logger):
        conf_filename = self.checkAlreadyTrainedConf(args)
        with open(conf_filename, 'r') as f:
            conf_json = json.load(f)
            conf = factory.fromJson(conf_json['classification_conf'],
                                    logger=logger)
            params = {}
            params['num_clusters'] = args.num_clusters
            params['num_results'] = None
            params['projection_conf'] = None
            params['label'] = 'all'
            clustering_conf = ClusteringConfFactory.getFactory().fromParam(
                    args.clustering_algo,
                    params,
                    logger=logger)
            alerts_conf = AlertsConfiguration(args.top_n_alerts,
                                              args.detection_threshold,
                                              clustering_conf,
                                              logger=logger)
            test_conf = ValidationDatasetConf(args.validation_dataset,
                                              alerts_conf=alerts_conf,
                                              logger=logger)
            conf.test_conf = test_conf
        return conf

    def setExperimentFromArgs(self, args):
        self.initExperiment(args.project, args.dataset,
                            experiment_name=args.exp_name)
        factory = ClassifierConfFactory.getFactory()
        if args.model == 'AlreadyTrained':
            self.already_trained = args.model_exp_id
            conf = self.generateAlreadyTrainedConf(factory, args,
                                                   self.logger)
        else:
            conf = factory.fromArgs(args.model, args, logger=self.logger)
        self.setConf(conf, args.features_file,
                     annotations_filename='ground_truth.csv')
        self.export()


ExperimentFactory.getFactory().registerClass('ClassificationExperiment',
                                             ClassificationExperiment)
