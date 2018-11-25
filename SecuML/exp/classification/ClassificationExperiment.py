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

import json
import os.path as path

from SecuML.core.classification.conf import ClassifierConfFactory
from SecuML.exp import db_tables
from SecuML.exp.tools import db_tools
from SecuML.exp import ExperimentFactory
from SecuML.exp.classification.RunClassifier import RunClassifier
from SecuML.exp.classification.ValidationExperiment import ValidationConf
from SecuML.exp.classification.ValidationExperiment import ValidationExperiment
from SecuML.exp.conf.AnnotationsConf import AnnotationsConf
from SecuML.exp.conf.DatasetConf import DatasetConf
from SecuML.exp.conf.FeaturesConf import FeaturesConf
from SecuML.exp.Experiment import Experiment
from SecuML.exp.tools.exp_exceptions import SecuMLexpException
from .ClassificationConf import ClassificationConf


class NoGroundTruth(SecuMLexpException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ExperimentNotFound(SecuMLexpException):

    def __init__(self, exp_id):
        self.exp_id = exp_id

    def __str__(self):
        return('The experiment %d cannot be found.' % (self.exp_id))


class InvalidModelExperimentKind(SecuMLexpException):

    def __init__(self, exp_kind):
        self.exp_kind = exp_kind

    def __str__(self):
        return('model-exp-id is a %s experiment '
               'while it must be a DIADEM or an ActiveLearning experiment.'
               % (self.exp_kind))


class ClassificationExperiment(Experiment):

    def create_exp(self):
        self.createTestExperiment()
        if self.exp_conf.already_trained is not None:
            self.setAlreadyTrainedCoreConf()
        Experiment.create_exp(self)

    def createTestExperiment(self):
        self.test_exp = None
        test_conf = self.exp_conf.core_conf.test_conf
        if test_conf.method == 'dataset':
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

    def run(self, datasets=None, cv_monitoring=False):
        Experiment.run(self)
        if datasets is None:
            datasets = self.generateDatasets()
        classifier_conf = self.exp_conf.core_conf.classifier_conf
        self.classifier = classifier_conf.model_class(classifier_conf)
        run_classifier = RunClassifier(self.classifier, datasets, self)
        run_classifier.run(cv_monitoring=cv_monitoring)

    def generateDatasets(self):
        instances = self.getInstances()
        test_instances = None
        test_conf = self.exp_conf.core_conf.test_conf
        if test_conf.method == 'dataset':
            test_instances = self.test_exp.getInstances()
        classifier_conf = self.exp_conf.core_conf.classifier_conf
        return test_conf.generateDatasets(classifier_conf, instances,
                                          test_instances)

    def webTemplate(self):
        return 'classification/main.html'

    def checkAlreadyTrainedConf(self):
        model_exp = db_tables.checkExperimentId(self.session,
                                                self.exp_conf.already_trained)
        # Check whether the experiment exists
        if model_exp is None:
            raise ExperimentNotFound(self.exp_conf.already_trained)
        # Check the type of the experiment
        if model_exp.kind not in ['Classification', 'ActiveLearning']:
            raise InvalidModelExperimentKind(model_exp.kind)
        exp_dir = Experiment.get_output_dir(self.exp_conf.secuml_conf,
                                            self.exp_conf.dataset_conf.project,
                                            self.exp_conf.dataset_conf.dataset,
                                            self.exp_conf.already_trained)
        if model_exp.kind == 'ActiveLearning':
            last_iter = db_tools.getCurrentIteration(
                                                self.session,
                                                self.exp_conf.already_trained)
            models_json = path.join(exp_dir, str(last_iter),
                                    'models_experiments.json')
            with open(models_json, 'r') as f:
                last_supervised_exp = json.load(f)['binary']
                self.exp_conf.already_trained = last_supervised_exp
            exp_dir = Experiment.get_output_dir(self.exp_conf.secuml_conf,
                                             self.exp_conf.dataset_conf.project,
                                             self.exp_conf.dataset_conf.dataset,
                                             self.exp_conf.already_trained)
        return path.join(exp_dir, 'conf.json')

    def setAlreadyTrainedCoreConf(self):
        conf_filename = self.checkAlreadyTrainedConf()
        with open(conf_filename, 'r') as f:
            conf_json = json.load(f)['core_conf']['classifier_conf']
            factory = ClassifierConfFactory.getFactory()
            conf = factory.from_json(conf_json, self.logger)
            self.exp_conf.core_conf.classifier_conf = conf


ExperimentFactory.getFactory().register('Classification',
                                        ClassificationExperiment,
                                        ClassificationConf)
