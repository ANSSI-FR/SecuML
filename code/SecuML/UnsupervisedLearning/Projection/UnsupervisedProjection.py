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

import abc
import copy
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from Projection import Projection

class UnsupervisedProjection(Projection):

    @abc.abstractmethod
    def setProjectionMatrix(self):
        return

    @abc.abstractmethod
    def setNumComponents(self):
        return

    def run(self, instances, quick = False):
        self.fit(instances, quick = quick)
        self.transform(instances, quick = quick)
    
    def getFittingInstances(self, instances):
        return instances

    def fit(self, instances, quick = False):
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('projection', self.projection)])
        instances_np = copy.deepcopy(instances.getFeatures())
        instances_np = np.array(instances_np)
        instances_np.flat[::instances_np.shape[1] + 1] += 0.01
        self.pipeline.fit(instances_np)
        self.setNumComponents()
        self.setProjectionMatrix()
        if not quick:
            self.printProjectionMatrixCSV(instances.getFeaturesNames())
