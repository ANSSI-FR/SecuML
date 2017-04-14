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
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from SecuML.Data.Instances       import Instances
from SecuML.Tools                import dir_tools

from Performance.PerformanceMonitoring import PerformanceMonitoring
from Visualization.Visualization import Visualization

class Projection(object):

    def __init__(self, experiment):
        self.experiment       = experiment
        self.conf             = experiment.conf
        self.num_components   = self.conf.num_components
        self.output_directory = dir_tools.getExperimentOutputDirectory(experiment)

    @abc.abstractmethod
    def setProjectionMatrix(self):
        return

    @abc.abstractmethod
    def generateInputParameters(self, instances):
        return

    def run(self, instances = None, visu = True, performance = False):
        if instances is None:
            instances = Instances()
            instances.initFromExperiment(self.experiment)
        self.fit(instances, visu = visu)
        self.transform(instances, visu = visu, performance = performance)

    @abc.abstractmethod
    def fit(self, instances, visu = True):
        return

    def transform(self, instances, visu = True, performance = False):
        projected_instances = Instances()
        projected_matrix = self.pipeline.transform(instances.getFeatures())
        projected_instances.initFromMatrix(
            instances.getIds(),
            projected_matrix,
            self.componentLabels(),
            labels = instances.getLabels(),
            families = instances.families,
            true_labels = instances.getLabels(true_labels = True),
            true_families = instances.getFamilies(true_labels = True),
            annotations = instances.annotations)
        if visu:
            visu = Visualization(self)
            visu.allHexBin(projected_instances)
        if performance:
            self.performance = self.assessPerformance(projected_instances)
        return projected_instances

    def assessPerformance(self, projected_instances):
        if not projected_instances.hasTrueLabels():
            return None
        evaluation = PerformanceMonitoring(self)
        evaluation.computePerformance(projected_instances)
        return evaluation

    def outputFilename(self, name, extension):
        output_filename =  self.output_directory
        output_filename += name
        output_filename += extension
        return output_filename

    ## Return the array ['C_i_min', ..., 'C_(i_max)']
    ## where the range i_max, i_max is determined by selected_components
    ## selected_components default value is range(num_components)
    def componentLabels(self, selected_components = None):
        if selected_components is None:
            selected_components = range(self.num_components)
        return ['C_' + str(x) for x in selected_components]

    def createPipeline(self):
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('projection', self.projection)])

    def featuresPreprocessing(self, instances):
        features = copy.deepcopy(instances.getFeatures())
        features = np.array(features)
        features.flat[::features.shape[1] + 1] += 0.01
        return features

    def printProjectionMatrixCSV(self, features_names):
        projection_matrix = pd.DataFrame(self.projection_matrix,
                columns = self.componentLabels(),
                index = features_names)
        projection_matrix.index.name = 'feature'
        projection_matrix.to_csv(
                self.outputFilename('projection_matrix', '.csv'),
                sep = ',',
                header = True,
                index = True)

    def setNumComponents(self):
        self.num_components = self.projection_matrix.shape[1]
