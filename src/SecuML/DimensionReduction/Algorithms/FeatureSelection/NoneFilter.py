## SecuML
## Copyright (C) 2017  ANSSI
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
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

import numpy as np

from sklearn.base import BaseEstimator
from sklearn.feature_selection.base import SelectorMixin

from UnsupervisedFeatureSelection import UnsupervisedFeatureSelection

class NoneFilter(UnsupervisedFeatureSelection):

    def __init__(self, conf):
        UnsupervisedFeatureSelection.__init__(self, conf)
        self.projection = NoneFilter_()

class NoneFilter_(BaseEstimator, SelectorMixin):

        def fit(self, X, y = None):
            num_features = X.shape[1]
            self.is_none = [True] * num_features
            for f in range(num_features):
                if (np.any(np.isnan(X[:, f]))):
                    self.is_none[f] = False
            return self

        def _get_support_mask(self):
            return np.array(self.is_none)

        def transform(self, X):
            return X[:, self.get_support()]

