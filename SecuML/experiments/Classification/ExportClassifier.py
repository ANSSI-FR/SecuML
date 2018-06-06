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

from sklearn.externals import joblib

from SecuML.core.Tools import dir_tools


class ExportClassifier(object):

    def __init__(self, classifier, output_directory, experiment):
        self.classifier = classifier
        self.output_directory = output_directory
        self.experiment = experiment

    def export(self, datasets):
        self.exportTraining()
        self.exportCrossValidation(datasets)
        self.exportTesting()
        self.exportAlerts(datasets)
        if datasets.validation_instances is not None:
            self.exportValidation()

    def exportTraining(self):
        self.classifier.training_monitoring.display(self.output_directory)
        self.dumpModel()

    def exportCrossValidation(self, datasets):
        if self.classifier.cv_monitoring:
            self.classifier.crossValidationMonitoring(datasets)
            self.classifier.cv_monitoring.display(self.output_directory)
        else:
            self.classifier.cv_monitoring = None

    def exportTesting(self):
        self.classifier.testing_monitoring.display(self.output_directory)

    def exportValidation(self):
        self.classifier.validation_monitoring.display(self.output_directory)

    def exportAlerts(self, datasets):
        if self.classifier.alerts is None:
            return
        alerts_directory = self.output_directory + 'alerts/'
        dir_tools.createDirectory(alerts_directory)
        self.classifier.alerts.export(alerts_directory)

    def dumpModel(self):
        # check added for Sssvdd that has no dump model function
        if self.classifier.pipeline is not None:
            model_dir = self.output_directory + 'model/'
            dir_tools.createDirectory(model_dir)
            joblib.dump(self.classifier.pipeline, model_dir + 'model.out')
