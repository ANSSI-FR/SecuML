# SecuML
# Copyright (C) 2018  ANSSI
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

from SecuML.core.ActiveLearning.UpdateModel import UpdateModel

from SecuML.experiments.Classification.ClassificationExperiment import ClassificationExperiment
from SecuML.experiments.Classification.RunClassifier import RunClassifier


class UpdateModelExp(UpdateModel):

    def __init__(self, iteration):
        UpdateModel.__init__(self, iteration)
        self.experiment = self.iteration.experiment

    def run(self):
        models_conf = self.iteration.conf.models_conf
        self.models_exp = {}
        for k, conf in models_conf.items():
            self.models_exp[k] = self.runModel(k, conf)
        self.exportModelsExperiments()

    def exportModelsExperiments(self):
        export_models = {}
        for k, exp in self.models_exp.items():
            export_models[k] = exp.experiment_id
        output_file = path.join(self.iteration.iteration_dir,
                                'models_experiments.json')
        with open(output_file, 'w') as f:
            json.dump(export_models, f, indent=2)

    def runModel(self, kind, conf):
        self.setDatasets(conf)

        # Create the experiment
        exp = self.experiment
        name = 'AL' + str(exp.experiment_id) + '-Iter'
        name += str(self.iteration.iteration_number) + '-' + kind
        model_exp = ClassificationExperiment(exp.project, exp.dataset, exp.session,
                                             experiment_name=name,
                                             parent=exp.experiment_id)
        model_exp.setConf(conf, exp.features_filename,
                          annotations_id=exp.annotations_id)
        model_exp.export()

        # Build the model
        model = conf.model_class(model_exp.conf, cv_monitoring=True)
        model_run = RunClassifier(model, self.datasets, model_exp)
        model_run.run()
        self.models[kind] = model

        # Execution time monitoring
        time = model.training_execution_time + model.testing_execution_time
        self.times[kind] = time

        return model_exp
