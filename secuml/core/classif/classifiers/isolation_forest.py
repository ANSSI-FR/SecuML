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
from sklearn.ensemble import IsolationForest as IsolationForestClassifier

from . import UnsupervisedClassifier


class _IsolationForest(IsolationForestClassifier):

    def predict_from_scores(self, X, scores):
        threshold = self.threshold_ if self.behaviour == 'old' else 0
        is_inlier = np.ones(X.shape[0], dtype=int)
        is_inlier[scores < threshold] = -1
        return is_inlier


class IsolationForest(UnsupervisedClassifier):

    def _get_pipeline(self):
        return [('model', _IsolationForest(n_jobs=self.conf.n_jobs,
                                           behaviour='new',
                                           contamination='auto'))]
