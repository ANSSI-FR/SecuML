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

from SecuML.SupervisedLearning.SupervisedLearningDatasets import SupervisedLearningDatasets

class TrainTestValidation(object):

    def __init__(self, iteration):
        self.iteration = iteration

    def run(self):
        datasets = SupervisedLearningDatasets(self.iteration.experiment)
        datasets.generateDatasets()
        datasets.setValidationInstances(self.iteration.datasets.validation_instances)
        model_class = self.iteration.experiment.supervised_learning_conf.model_class
        self.classifier = model_class(self.iteration.experiment, datasets,
                output_directory = self.iteration.output_directory)
        self.classifier.run()

        self.training_predicting_time  = self.classifier.training_execution_time
        self.training_predicting_time += self.classifier.testing_execution_time
