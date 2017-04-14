## SecuML
## Copyright (C) 2016  ANSSI
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

import copy

from SecuML.Experiment.ClassificationExperiment import ClassificationExperiment
from SecuML.Classification.ClassifierDatasets import ClassifierDatasets

class TrainTestValidation(object):

    def __init__(self, iteration):
        self.iteration = iteration

    def run(self):
        self.setDatasets()
        self.binaryClassifier()
        if self.iteration.experiment.conf.labeling_method == 'Aladin':
            self.multilabelClassifier()
        else:
            self.multilabel_classifier = None

    def setDatasets(self):
        al_datasets = self.iteration.datasets
        self.datasets = ClassifierDatasets(self.iteration.experiment)
        self.datasets.setDatasets(al_datasets.getTrainInstances(), al_datasets.getTestInstances())
        self.datasets.setValidationInstances(al_datasets.validation_instances)

    def binaryClassifier(self):
        # Create the binary experiment
        exp = self.iteration.experiment
        name = 'AL' + str(exp.experiment_id) + '-Iter' + str(self.iteration.iteration_number) + '-BinaryClassifier'
        binary_exp = ClassificationExperiment(exp.project, exp.dataset, exp.db, exp.cursor,
                experiment_name = name,
                experiment_label = exp.experiment_label,
                parent = exp.experiment_id)
        binary_exp.setFeaturesFilenames(exp.features_filenames)
        binary_conf = exp.classification_conf
        binary_exp.setClassifierConf(binary_conf)
        binary_exp.createExperiment()
        binary_exp.export()
        # Build the binary classifier
        model_class = exp.classification_conf.model_class
        self.binary_classifier = model_class(binary_exp, self.datasets)
        self.binary_classifier.run()
        # Execution time monitoring
        self.training_predicting_time  = self.binary_classifier.training_execution_time
        self.training_predicting_time += self.binary_classifier.testing_execution_time

    def multilabelClassifier(self):
        # Create the multi-label experiment
        exp = self.iteration.experiment
        name = 'AL' + str(exp.experiment_id) + '-Iter' + str(self.iteration.iteration_number) + '-MultilabelClassifier'
        multilabel_exp = ClassificationExperiment(exp.project, exp.dataset, exp.db, exp.cursor,
                experiment_name = name,
                experiment_label = exp.experiment_label,
                parent = exp.experiment_id)
        multilabel_exp.setFeaturesFilenames(exp.features_filenames)
        multilabel_conf = copy.deepcopy(exp.classification_conf)
        multilabel_conf.families_supervision = True
        multilabel_exp.setClassifierConf(multilabel_conf)
        multilabel_exp.createExperiment()
        multilabel_exp.export()
        # Train the multilabel classifier
        model_class = exp.classification_conf.model_class
        self.multilabel_classifier = model_class(multilabel_exp, self.datasets)
        self.multilabel_classifier.run()
