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
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

import abc
import copy
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from SecuML.Data.Instances import Instances

from Performance.PerformanceMonitoring import PerformanceMonitoring
from Visualization.Visualization import Visualization

class DimensionReduction(object):

    def __init__(self, conf):
        self.conf = conf

    @abc.abstractmethod
    def generateInputParameters(self, instances):
        return

    @abc.abstractmethod
    def componentLabels(self, features_names):
        return

    @abc.abstractmethod
    def setNumComponents(self):
        return

    @abc.abstractmethod
    def createPipeline(self):
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('projection', self.projection)])

    @abc.abstractmethod
    def fit(self, instances):
        return

    def transform(self, instances):
        projected_matrix = self.pipeline.transform(instances.getFeatures())
        projected_instances = Instances(instances.getIds(),
                                        projected_matrix,
                                        self.componentLabels(instances.getFeaturesNames()),
                                        instances.labels,
                                        instances.families,
                                        instances.true_labels,
                                        instances.true_families,
                                        instances.annotations)
        return projected_instances

    def featuresPreprocessing(self, instances):
        features = copy.deepcopy(instances.getFeatures())
        features = np.array(features)
        features.flat[::features.shape[1] + 1] += 0.01
        return features

    def exportFit(self, experiment, instances):
        self.exportProjectionMatrix(experiment, instances.getFeaturesNames())

    def exportTransform(self, experiment, instances, projected_instances):
        visu = Visualization(self, experiment)
        visu.allHexBin(projected_instances)
        self.assessPerformance(experiment, projected_instances)

    def assessPerformance(self, experiment, projected_instances):
        if not projected_instances.hasTrueLabels():
            return None
        evaluation = PerformanceMonitoring(self, experiment)
        evaluation.computePerformance(projected_instances)
        return evaluation

    def exportProjectionMatrix(self, experiment, features_names):
        projection_matrix = pd.DataFrame(self.projection_matrix,
                columns = self.componentLabels(features_names),
                index = features_names)
        projection_matrix.index.name = 'feature'
        projection_matrix.to_csv(
                experiment.getOutputDirectory() + 'projection_matrix.csv',
                sep = ',',
                header = True,
                index = True)
