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


class UpdateModel(object):

    def __init__(self, iteration):
        self.iteration = iteration
        self.models = {}
        self.times = {}

    def run(self):
        models_conf = self.iteration.conf.models_conf
        for k, classification_conf in models_conf.items():
            self.runModel(k, classification_conf.classifier_conf)

    def runModel(self, kind, classifier_conf):
        al_datasets = self.iteration.datasets
        self.datasets = al_datasets.get_classifier_datasets(classifier_conf)
        model = classifier_conf.model_class(classifier_conf)
        model.trainTestValidation(self.datasets)
        self.models[kind] = model
        # Execution time monitoring
        time = model.training_execution_time + model.testing_execution_time
        self.times[kind] = time
        return None
