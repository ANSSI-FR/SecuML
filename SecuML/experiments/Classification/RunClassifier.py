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

import os.path as path

from .ExportClassifier import ExportClassifier

from SecuML.core.Classification.Monitoring.CvMonitoring import CvMonitoring
from SecuML.experiments.Tools import dir_exp_tools


class RunClassifier(object):

    def __init__(self, classifier, datasets, experiment):
        self.classifier = classifier
        self.datasets = datasets
        self.experiment = experiment

    def run(self):
        test_conf = self.classifier.conf.test_conf
        if test_conf.method in ['cv', 'temporal_cv', 'sliding_window']:
            self.runCrossValidation()
        else:
            self.runOneFold(self.datasets)

    def runCrossValidation(self):
        test_conf = self.classifier.conf.test_conf
        if test_conf.method == 'cv':
            global_cv_monitoring = CvMonitoring(self.classifier.conf,
                                                num_folds=test_conf.num_folds)
            global_cv_monitoring.initMonitorings(self.datasets)
        else:
            global_cv_monitoring = None
        for fold_id, datasets in enumerate(self.datasets.datasets):
            self.runOneFold(datasets, fold_id=fold_id)
            coefficients = None
            if not self.classifier.conf.families_supervision:
                coefficients = self.classifier.training_monitoring.coefficients.coef_summary['mean']
            if test_conf.method == 'cv':
                global_cv_monitoring.addFold(fold_id,
                                             self.classifier.testing_predictions,
                                             coefficients)
        if test_conf.method == 'cv':
            global_cv_monitoring.display(self.experiment.getOutputDirectory())

    def trainTestValidation(self, datasets):
        if self.experiment.already_trained is not None:
            exp_dir = dir_exp_tools.getExperimentOutputDirectory(
                    self.experiment.secuml_conf,
                    self.experiment.project,
                    self.experiment.dataset,
                    self.experiment.already_trained)
            model_filename = path.join(exp_dir, 'model', 'model.out')
            self.classifier.loadModel(model_filename)
            self.classifier.testValidation(datasets)
        else:
            self.classifier.trainTestValidation(datasets)

    def export(self, datasets, fold_id):
        output_directory = self.experiment.getOutputDirectory()
        if fold_id is not None:
            output_directory = path.join(output_directory, str(fold_id))
        export_classifier = ExportClassifier(self.classifier, output_directory,
                                             self.experiment)
        export_classifier.export(datasets)

    def runOneFold(self, datasets, fold_id=None):
        self.trainTestValidation(datasets)
        self.export(datasets, fold_id)
