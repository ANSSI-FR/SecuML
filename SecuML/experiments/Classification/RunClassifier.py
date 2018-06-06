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

from SecuML.core.Classification.Monitoring.CvMonitoring import CvMonitoring
from .ExportClassifier import ExportClassifier


class RunClassifier(object):

    def __init__(self, classifier, datasets, experiment):
        self.classifier = classifier
        self.datasets = datasets
        self.experiment = experiment

    def run(self):
        test_conf = self.classifier.conf.test_conf
        if test_conf.method == 'cv':
            global_cv_monitoring = CvMonitoring(self.classifier.conf,
                                                num_folds=test_conf.num_folds)
            global_cv_monitoring.initMonitorings(self.datasets)
            for fold_id, datasets in enumerate(self.datasets.datasets):
                self.runOneFold(datasets, fold_id=fold_id)
                coefficients = None
                if not self.classifier.conf.families_supervision:
                    coefficients = self.classifier.training_monitoring.coefficients.coef_summary[
                        'mean']
                global_cv_monitoring.addFold(fold_id,
                                             self.classifier.testing_predictions,
                                             coefficients)
            global_cv_monitoring.display(self.experiment.getOutputDirectory())
        else:
            self.runOneFold(self.datasets)

    def runOneFold(self, datasets, fold_id=None):
        self.classifier.trainTestValidation(datasets)
        output_directory = self.experiment.getOutputDirectory()
        if fold_id is not None:
            output_directory += str(fold_id) + '/'
        export_classifier = ExportClassifier(self.classifier, output_directory,
                                             self.experiment)
        export_classifier.export(datasets)
