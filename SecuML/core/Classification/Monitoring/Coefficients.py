# SecuML
# Copyright (C) 2016  ANSSI
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

from SecuML.core.Tools import matrix_tools


class Coefficients(object):

    # One line for each fold
    # And mean, std, Zscore
    def __init__(self, num_folds, features):
        self.fold_coef = pd.DataFrame(
            np.zeros((num_folds, len(features))),
            index=['f_' + str(x) for x in range(num_folds)],
            columns=features)

    def addFold(self, fold_id, coef):
        self.fold_coef.iloc[fold_id, :] = coef

    def finalComputations(self):
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

    def display(self, directory):
        with open(directory + 'model_coefficients.csv', 'w') as f:
            matrix_tools.sortDataFrame(
                self.coef_summary, 'abs_mean', False, True)
            self.coef_summary.to_csv(f, index_label='feature')
