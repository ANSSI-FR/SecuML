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
from sklearn import svm
from sklearn.preprocessing import StandardScaler

from . import SupervisedClassifier


class _Svc(svm.SVC):

    def predict_from_probas(self, X, probas):
        if probas.shape[1] == 1:
            indices = (probas[:, 1] > 0.5).astype(np.int)
        else:
            indices = probas.argmax(axis=1)
        return self.classes_[indices]


class Svc(SupervisedClassifier):

    def _get_pipeline(self):
        return [('scaler', StandardScaler()),
                ('model', _Svc(kernel='linear', probability=True))]
