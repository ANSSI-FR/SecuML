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

import numpy as np
import pandas as pd

class Coefficients(object):

    ## One line for each fold
    ## And mean, std, Zscore
    def __init__(self, num_folds, features):
        self.fold_coef = pd.DataFrame(
                np.zeros((num_folds, len(features))),
                index = ['f_' + str(x) for x in range(num_folds)],
                columns = features)

    def addFold(self, fold_id, coef):
        self.fold_coef.iloc[fold_id,:] = coef

    def finalComputations(self):
        features = self.fold_coef.columns
        columns = ['mean', 'std', 'Zscore', 'abs_mean']
        self.coef_summary = pd.DataFrame(
                np.zeros((len(features), len(columns))),
                columns = columns,
                index = features)
        coef_mean = self.fold_coef.mean(axis = 0)
        coef_std  =  self.fold_coef.std(axis = 0)
        self.coef_summary.loc[:,'mean'] = coef_mean
        self.coef_summary.loc[:,'abs_mean'] = map(abs, coef_mean)
        self.coef_summary.loc[:,'std']  = coef_std
        coef_std = [0.00001 if x == 0 else x for x in coef_std]
        self.coef_summary.loc[:,'Zscore'] = abs(coef_mean / coef_std)

    def display(self, directory):
        with open(directory + 'model_coefficients.csv', 'w') as f:
            if pd.__version__ in ['0.13.0', '0.14.1']:
                self.coef_summary.sort(['abs_mean'],
                        ascending = [False], inplace = True)
            else:
                self.coef_summary.sort_values(['abs_mean'],
                        ascending = [False], inplace = True)
            self.coef_summary.to_csv(f, index_label = 'feature')
