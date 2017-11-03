## SecuML
## Copyright (C) 2017  ANSSI
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

from UpdateModel import UpdateModel

class UpdateModelExp(UpdateModel):

    def __init__(self, iteration):
        UpdateModel.__init__(self, iteration)
        self.experiment = self.iteration.experiment

    def run(self):
        models_conf = self.iteration.conf.models_conf
        self.models_exp = {}
        for k, conf in models_conf.iteritems():
            self.models_exp[k] = self.runModel(k, conf)
        self.exportModelsExperiments()

    def exportModelsExperiments(self):
        export_models = {}
        for k, exp in self.models_exp.iteritems():
            export_models[k] = exp.experiment_id
        output_file  = self.iteration.iteration_dir
        output_file += 'models_experiments.json'
        with open(output_file, 'w') as f:
            json.dump(export_models, f, indent = 2)

    def runModel(self, kind, conf):
        self.setDatasets(conf)

        # Create the experiment
        exp = self.experiment
        name  = 'AL' + str(exp.experiment_id) + '-Iter'
        name += str(self.iteration.iteration_number) + '-' + kind
        model_exp = ClassificationExperiment(exp.project, exp.dataset, exp.session,
                                             experiment_name = name,
                                             labels_id = exp.labels_id,
                                             parent = exp.experiment_id)
        model_exp.setFeaturesFilenames(exp.features_filenames)
        model_exp.setClassifierConf(conf)
        model_exp.createExperiment()
        model_exp.export()

        # Build the model
        model = conf.model_class(model_exp.classification_conf, self.datasets,
                                 cv_monitoring = True)
        model.run(model_exp.getOutputDirectory(), model_exp)
        self.models[kind] = model

        # Execution time monitoring
        time  = model.training_execution_time + model.testing_execution_time
        self.times[kind] = time

        return model_exp
