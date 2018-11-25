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

from SecuML.core.active_learning.UpdateModel import UpdateModel

from SecuML.exp.classification.ClassificationConf \
        import ClassificationConf
from SecuML.exp.classification.ClassificationExperiment \
        import ClassificationExperiment


class UpdateModelExp(UpdateModel):

    def __init__(self, iteration):
        UpdateModel.__init__(self, iteration)
        self.experiment = self.iteration.experiment

    def run(self):
        models_conf = self.iteration.conf.models_conf
        self.models_exp = {}
        for k, classification_conf in models_conf.items():
            self.models_exp[k] = self.runModel(k, classification_conf)
        self.exportModelsExperiments()

    def exportModelsExperiments(self):
        export_models = {}
        for k, exp in self.models_exp.items():
            export_models[k] = exp.experiment_id
        output_file = path.join(self.iteration.iteration_dir,
                                'models_experiments.json')

        with open(output_file, 'w') as f:
            json.dump(export_models, f, indent=2)

    def runModel(self, kind, classification_conf):
        al_datasets = self.iteration.datasets
        classifier_conf = classification_conf.classifier_conf
        self.datasets = al_datasets.get_classifier_datasets(classifier_conf)
        # Create the experiment
        exp = self.experiment
        name = 'AL%d-Iter%d-%s' % (exp.experiment_id,
                                   self.iteration.iteration_number,
                                   kind)
        exp_conf = ClassificationConf(exp.exp_conf.secuml_conf,
                                      exp.exp_conf.dataset_conf,
                                      exp.exp_conf.features_conf,
                                      exp.exp_conf.annotations_conf,
                                      classification_conf,
                                      experiment_name=name,
                                      parent=exp.experiment_id)
        exp_conf.test_exp_conf = exp.exp_conf.test_exp_conf
        model_exp = ClassificationExperiment(exp_conf, session=exp.session)
        model_exp.create_exp()
        model_exp.run(datasets=self.datasets, cv_monitoring=True)
        self.models[kind] = model_exp.classifier

        # Execution time monitoring
        time  = model_exp.classifier.training_execution_time
        time += model_exp.classifier.testing_execution_time
        self.times[kind] = time

        return model_exp
