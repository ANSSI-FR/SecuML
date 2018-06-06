# SecuML
# Copyright (C) 2017-2018  ANSSI
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
import copy
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from SecuML.core.Data.Instances import Instances

from .Performance.PerformanceMonitoring import PerformanceMonitoring
from .Visualization.Visualization import Visualization


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
        projected_matrix = self.pipeline.transform(
            instances.features.getValues())
        projected_instances = Instances(instances.ids.getIds(),
                                        projected_matrix,
                                        self.componentLabels(
                                            instances.features.getNames()),
                                        self.componentLabels(
                                            instances.features.getNames()),
                                        instances.annotations.getLabels(),
                                        instances.annotations.getFamilies(),
                                        instances.ground_truth.getLabels(),
                                        instances.ground_truth.getFamilies())
        return projected_instances

    def featuresPreprocessing(self, instances):
        features = copy.deepcopy(instances.features.getValues())
        features = np.array(features)
        features.flat[::features.shape[1] + 1] += 0.01
        return features

    ####################
    # Export function ##
    ####################

    def exportFit(self, output_directory, instances):
        self.exportProjectionMatrix(
            output_directory, instances.features.getNames())

    def exportTransform(self, output_directory, instances, projected_instances):
        visu = Visualization(self, output_directory)
        visu.allHexBin(projected_instances)
        self.assessPerformance(output_directory, projected_instances)

    def assessPerformance(self, output_directory, projected_instances):
        if not projected_instances.hasGroundTruth():
            return None
        evaluation = PerformanceMonitoring(self)
        evaluation.computePerformance(projected_instances)
        return evaluation

    def exportProjectionMatrix(self, output_directory, features_names):
        projection_matrix = pd.DataFrame(self.projection_matrix,
                                         columns=self.componentLabels(
                                             features_names),
                                         index=features_names)
        projection_matrix.index.name = 'feature'
        projection_matrix.to_csv(
            output_directory + 'projection_matrix.csv',
            sep=',',
            header=True,
            index=True)
