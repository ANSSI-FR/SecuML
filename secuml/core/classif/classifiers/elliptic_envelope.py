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
from sklearn.covariance import EllipticEnvelope as EllipticEnvelopeClassifier
from sklearn.preprocessing import StandardScaler

from . import UnsupervisedClassifier


class _EllipticEnvelope(EllipticEnvelopeClassifier):

    def predict_from_scores(self, X, scores):
        is_inlier = np.full(X.shape[0], -1, dtype=int)
        is_inlier[scores >= 0] = 1
        return is_inlier


class EllipticEnvelope(UnsupervisedClassifier):

    def _get_pipeline(self):
        return [('scaler', StandardScaler()),
                ('model', _EllipticEnvelope())]
