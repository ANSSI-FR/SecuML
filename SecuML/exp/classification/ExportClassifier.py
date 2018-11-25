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

import shutil
import os.path as path

from SecuML.core.tools import dir_tools
from SecuML.exp.Experiment import Experiment


class ExportClassifier(object):

    def __init__(self, classifier, output_dir, exp, test_exp):
        self.classifier = classifier
        self._set_output_dir(output_dir, test_exp)
        self.output_dir = output_dir
        self.exp = exp
        self.exp_conf = exp.exp_conf

    def _set_output_dir(self, output_dir, test_exp):
        self.output_dir = output_dir
        self.val_output_dir = output_dir

    def export(self):
        self.exportTraining()
        self.exportCrossValidation()
        self.exportTesting()
        self.exportAlerts()
        self.exportValidation()

    def exportTraining(self):
        already_trained = self.exp.exp_conf.already_trained
        if already_trained is None:
            self.classifier.training_monitoring.display(self.output_dir)
            self.dumpModel()
        else:
            src_dir = Experiment.get_output_dir(self.exp_conf.secuml_conf,
                                             self.exp_conf.dataset_conf.project,
                                             self.exp_conf.dataset_conf.dataset,
                                             already_trained)
            for d in ['train', 'model']:
                shutil.copytree(path.join(src_dir, d),
                                path.join(self.output_dir, d))

    def exportCrossValidation(self):
        if self.classifier.cv_monitoring is not None:
            self.classifier.cv_monitoring.display(self.output_dir)

    def exportTesting(self):
        self.classifier.testing_monitoring.display(self.val_output_dir)

    def exportValidation(self):
        if self.classifier.validation_monitoring is not None:
            self.classifier.validation_monitoring.display(self.val_output_dir)

    def exportAlerts(self):
        if self.exp.alerts is None:
            return
        alerts_directory = path.join(self.output_dir, 'alerts')
        dir_tools.createDirectory(alerts_directory)
        self.exp.alerts.export(alerts_directory)

    def dumpModel(self):
        # check added for Sssvdd that has no dump model function
        if self.classifier.pipeline is not None:
            model_dir = path.join(self.output_dir, 'model')
            dir_tools.createDirectory(model_dir)
            self.classifier.dumpModel(path.join(model_dir, 'model.out'))
