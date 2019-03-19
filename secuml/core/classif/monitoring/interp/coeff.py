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


class Coefficients(object):

    # One line for each fold
    # And mean, std, Zscore
    def __init__(self, features_info, num_folds=1):
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
        with open(path.join(directory, 'model_coefficients.csv'), 'w') as f:
            self.coef_summary.to_csv(f, index_label='feature')
