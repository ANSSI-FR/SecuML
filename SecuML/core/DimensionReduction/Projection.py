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

import abc
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .DimensionReduction import DimensionReduction


class Projection(DimensionReduction):

    def __init__(self, conf):
        DimensionReduction.__init__(self, conf)

    @abc.abstractmethod
    def setProjectionMatrix(self):
        return

    @abc.abstractmethod
    def generateInputParameters(self, instances):
        return

    @abc.abstractmethod
    def fit(self, instances):
        return

    def createPipeline(self):
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('projection', self.projection)])

    def componentLabels(self, features_names):
        return ['C_' + str(x) for x in range(self.num_components)]

    def setNumComponents(self):
        self.num_components = self.projection_matrix.shape[1]
