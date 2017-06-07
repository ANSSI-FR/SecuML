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

import json

from SecuML.Experiment.ClassificationExperiment import ClassificationExperiment
from SecuML.Classification.ClassifierDatasets import ClassifierDatasets

class TrainTestValidation(object):

    def __init__(self, iteration):
        self.iteration = iteration
        self.models = {}
        self.times = {}

    def run(self):
        models_conf = self.iteration.experiment.conf.models_conf
        for k, conf in models_conf.iteritems():
            self.runModel(k, conf)
        self.exportModelsExperiments()

    def runModel(self, kind, conf):
        self.setDatasets(conf)
        # Create the experiment
        exp = self.iteration.experiment
        name = 'AL' + str(exp.experiment_id) + '-Iter' + str(self.iteration.iteration_number) + '-' + kind
        model_exp = ClassificationExperiment(exp.project, exp.dataset, exp.db, exp.cursor,
                experiment_name = name,
                experiment_label = exp.experiment_label,
                parent = exp.experiment_id)
        model_exp.setFeaturesFilenames(exp.features_filenames)
        model_exp.setClassifierConf(conf)
        model_exp.createExperiment()
        model_exp.export()
        # Build the model
        model = conf.model_class(model_exp, self.datasets, cv_monitoring = True)
        model.run()
        self.models[kind] = model
        # Execution time monitoring
        time  = model.training_execution_time + model.testing_execution_time
        self.times[kind] = time

    def setDatasets(self, conf):
        al_datasets = self.iteration.datasets
        self.datasets = ClassifierDatasets(self.iteration.experiment, conf)
        self.datasets.setDatasets(al_datasets.getTrainInstances(conf), al_datasets.getTestInstances())
        self.datasets.setValidationInstances(al_datasets.validation_instances)

    def exportModelsExperiments(self):
        models_exp = {}
        for k, model in self.models.iteritems():
            models_exp[k] = model.experiment.experiment_id
        output_file  = self.iteration.output_directory
        output_file += 'models_experiments.json'
        with open(output_file, 'w') as f:
            json.dump(models_exp, f, indent = 2)
