# SecuML
# Copyright (C) 2016-2019  ANSSI
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

import joblib
import json
import os.path as path

from .interp.coeff import Coefficients


class ClassifierMonitoring(object):

    def __init__(self, exp, num_folds=1):
        self.exp = exp
        self.num_folds = num_folds
        self.pipelines = [None for _ in range(self.num_folds)]
        self.exec_times = None
        self.class_labels = None
        self.coefficients = None

    def set_classifier(self, classifier, exec_times, fold_id=0):
        self.pipelines[fold_id] = classifier.pipeline
        if self.exec_times is None:
            self.exec_times = exec_times
        else:
            self.exec_times.add(exec_times)
        self.class_labels = classifier.class_labels
        self.set_coefficients(classifier, fold_id)

    def set_coefficients(self, classifier, fold_id):
        coefs = classifier.get_coefs()
        if coefs is not None:
            if self.coefficients is None:
                self.coefficients = Coefficients(self.exp, classifier.conf,
                                                 classifier.class_labels,
                                                 num_folds=self.num_folds)
            self.coefficients.add_fold(coefs, fold_id=fold_id)

    def final_computations(self):
        if self.coefficients is not None:
            self.coefficients.final_computations()

    def display(self, directory):
        self._export_pipelines(directory)
        self._export_class_labels(directory)
        self._export_exec_times(directory)
        if self.coefficients is not None:
            self.coefficients.display(directory)

    def _export_pipelines(self, directory):
        if self.num_folds == 1:
            joblib.dump(self.pipelines[0], path.join(directory, 'model.out'))
        else:
            for fold_id, pipeline in enumerate(self.pipelines):
                joblib.dump(pipeline, path.join(directory,
                                                'model_%i.out' % fold_id))

    def _export_class_labels(self, directory):
        class_labels = self.class_labels
        if class_labels is not None:
            class_labels = list(class_labels)
        with open(path.join(directory, 'class_labels.json'), 'w') as f:
            json.dump({'class_labels': class_labels}, f, indent=2)

    def _export_exec_times(self, directory):
        with open(path.join(directory, 'exec_times.json'), 'w') as f:
            json.dump(self.exec_times.__dict__, f, indent=2)
