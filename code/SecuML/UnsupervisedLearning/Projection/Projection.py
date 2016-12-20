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
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from SecuML.Data.Instances         import Instances
from SecuML.Plots.HexagonalBinning import HexagonalBinning
from SecuML.Tools                  import dir_tools

class Projection(object):

    def __init__(self, experiment):
        self.experiment = experiment
        self.num_components = self.experiment.conf.num_components
        self.setOutputDirectory()

    @abc.abstractmethod
    def setProjectionMatrix(self):
        return

    @abc.abstractmethod
    def setNumComponents(self, num_components = None):
        return

    @abc.abstractmethod
    def run(self, instances, quick = False):
        return

    @abc.abstractmethod
    def fit(self, instances, quick = False):
        return
    
    @abc.abstractmethod
    def getFittingInstances(self, instances):
        return

    def transform(self, instances, quick = False):
        projected_instances = Instances()
        projected_matrix = self.pipeline.transform(instances.getFeatures())
        projected_instances.initFromMatrix(
            instances.getIds(),
            projected_matrix,
            self.componentLabels(),
            labels = instances.getLabels(),
            sublabels = instances.sublabels,
            true_labels = instances.getLabels(true_labels = True),
            true_sublabels = instances.getSublabels(true_labels = True))
        if not quick:
            self.printAllProjectedInstancesHexbin(projected_instances)
        return projected_instances

    def setOutputDirectory(self):
        self.output_directory = dir_tools.getExperimentOutputDirectory(
                self.experiment)

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

    #####################
    # Projection Matrix #
    #####################

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

    ####################
    # Hexagonal Bining #
    ####################
    
    def printAllProjectedInstancesHexbin(self, projected_instances):
        #has_true_labels = projected_instances.hasTrueLabels()
        #malicious_ids = projected_instances.getMaliciousIds(true_labels = has_true_labels)
        malicious_ids = projected_instances.getMaliciousIds()
        num_max_components = 10
        num_components = num_max_components if self.num_components > num_max_components \
                else self.num_components
        for i in range(num_components - 1):
            for j in range(i+1, num_components):
                self.printProjectedInstancesHexbin(projected_instances, i, j, 
                        malicious_ids)

    ## Algorithm from 'Scatterplot matrix techniques for large N'
    ## by Carr, Littlefield, Nicholson, and Littlefield
    def printProjectedInstancesHexbin(self, projected_instances, cx_index, cy_index,
            malicious_ids):
        x = projected_instances.getFeatureValues('C_' + str(cx_index))
        y = projected_instances.getFeatureValues('C_' + str(cy_index))
        hex_bin = HexagonalBinning(x, y,
                projected_instances.getIds(), 30, malicious_ids)
        hex_bin.computeBinning()
        output_file = self.outputFilename(
          'c_'+ str(cx_index) + '_' + str(cy_index) + '_hexbin',
          '.json')
        hex_bin.printBinning(cx_index, cy_index, output_file)
