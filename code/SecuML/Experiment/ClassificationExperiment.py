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
from sklearn.externals import joblib

from SecuML.Classification.Configuration import ClassifierConfFactory
from SecuML.Classification.ClassifierDatasets import ClassifierDatasets

import ExperimentFactory
from Experiment import Experiment
from InstancesFromExperiment import InstancesFromExperiment

class ClassificationExperiment(Experiment):

    def __init__(self, project, dataset, session, experiment_name = None,
                 labels_id = None, parent = None):
        Experiment.__init__(self, project, dataset, session,
                            experiment_name = experiment_name,
                            labels_id = labels_id,
                            parent = parent)
        self.kind = 'Classification'

    def run(self):
        instances = InstancesFromExperiment(self).getInstances()
        test_instances = None
        if self.classification_conf.test_conf.method == 'test_dataset':
            test_exp = self.classification_conf.test_conf.test_exp
            test_instances = InstancesFromExperiment(test_exp).getInstances()
        datasets = ClassifierDatasets(self.classification_conf)
        datasets.generateDatasets(instances, test_instances)
        learning = self.classification_conf.model_class(self.classification_conf, datasets)
        learning.run(self.getOutputDirectory(), self)

    def setClassifierConf(self, classification_conf):
        self.classification_conf = classification_conf

    def generateSuffix(self):
        suffix  = self.classification_conf.generateSuffix()
        return suffix

    def getModelPipeline(self):
        experiment_dir = self.getOutputDirectory()
        pipeline = joblib.load(experiment_dir + '/model/model.out')
        return pipeline

    def getTopFeatures(self):
        experiment_dir = self.getOutputDirectory()
        pipeline = joblib.load(experiment_dir + '/model/model.out')
        if self.classification_conf.feature_importance == 'weight':
            return pipeline.named_steps['model'].coef_[0]
        elif self.classification_conf.feature_importance == 'score':
            return pipeline.named_steps['model'].feature_importances_
        else:
            raise ValueError('')

    @staticmethod
    def fromJson(obj, session):
        experiment = ClassificationExperiment(obj['project'], obj['dataset'], session)
        Experiment.expParamFromJson(experiment, obj)
        classification_conf = ClassifierConfFactory.getFactory().fromJson(
                obj['classification_conf'], experiment)
        experiment.setClassifierConf(classification_conf)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ClassificationExperiment'
        conf['classification_conf'] = self.classification_conf.toJson()
        return conf

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(
                description = 'Learn a detection model. ' +
                'The labels must be stored in labels/true_labels.csv.')
        Experiment.projectDatasetFeturesParser(parser)
        models = ['LogisticRegression', 'Svc', 'GaussianNaiveBayes',
                  'DecisionTree', 'RandomForest']
        subparsers = parser.add_subparsers(dest = 'model')
        factory = ClassifierConfFactory.getFactory()
        for model in models:
            model_parser = subparsers.add_parser(model)
            factory.generateParser(model, model_parser)
        return parser

    def webTemplate(self):
        return 'Classification/classification.html'

    def setExperimentFromArgs(self, args):
        self.setFeaturesFilenames(args.features_files)
        factory = ClassifierConfFactory.getFactory()
        conf = factory.fromArgs(args.model, args, self)
        self.setClassifierConf(conf)
        try:
            self.initLabels(args.labels)
        except Exception as e:
            message  = 'The ground truth labels must be provided in true_labels.csv '
            message += 'to run SecuML_classification.'
            print message
            raise e
        self.export()

ExperimentFactory.getFactory().registerClass('ClassificationExperiment',
                                             ClassificationExperiment)
