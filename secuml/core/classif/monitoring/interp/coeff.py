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

import numpy as np
import pandas as pd
import os.path as path

from secuml.core.tools.matrix import sort_data_frame


class ClassCoefficients(object):

    # One line for each fold
    # And mean, std, Zscore
    def __init__(self, features_info, class_label, num_folds=1):
        self.class_label = class_label
        self.fold_coef = pd.DataFrame(
                                  np.zeros((num_folds,
                                            features_info.num_features())),
                                  index=['f_%d' % x for x in range(num_folds)],
                                  columns=features_info.ids)

    def add_fold(self, coef, fold_id=0):
        self.fold_coef.iloc[fold_id, :] = coef

    def final_computations(self):
        features = self.fold_coef.columns
        mean = self.fold_coef.mean(axis=0)
        abs_mean = list(map(abs, mean))
        std = self.fold_coef.std(axis=0)
        zscore = abs(mean / [0.00001 if x == 0 else x for x in std])
        self.coef_summary = pd.DataFrame({'mean': mean,
                                          'std': std,
                                          'Zscore': zscore,
                                          'abs_mean': abs_mean},
                                         index=features)
        sort_data_frame(self.coef_summary, 'abs_mean', False, True)

    def display(self, directory):
        self.final_computations()
        if self.class_label is None:
            filename = 'model_coefficients.csv'
        else:
            filename = 'model_coefficients_%s.csv' % self.class_label
        with open(path.join(directory, filename), 'w') as f:
            self.coef_summary.to_csv(f, index_label='feature')


class Coefficients(object):

    def __init__(self, features_info, class_labels, num_folds=1):
        self.class_labels = class_labels
        self._init_class_coefficients(features_info, num_folds)

    def add_fold(self, coef, fold_id=0):
        if self.class_labels is None:
            self.coefficients.add_fold(coef[0], fold_id=fold_id)
        else:
            if len(self.class_labels) == 2:
                coef = np.vstack((coef, -coef[0]))
            for i, class_label in enumerate(self.class_labels):
                self.coefficients[class_label].add_fold(coef[i],
                                                        fold_id=fold_id)

    def display(self, directory):
        if self.class_labels is None:
            self.coefficients.display(directory)
        else:
            for _, coefficients in self.coefficients.items():
                coefficients.display(directory)

    def _init_class_coefficients(self, features_info, num_folds):
        if self.class_labels is None:
            self.coefficients = ClassCoefficients(features_info, None,
                                                  num_folds=num_folds)
        else:
            self.coefficients = {label: ClassCoefficients(features_info, label,
                                                          num_folds=num_folds)
                                 for label in self.class_labels}
