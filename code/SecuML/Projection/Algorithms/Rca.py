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
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

import metric_learn
import numpy as np

from SemiSupervisedProjection import SemiSupervisedProjection, FewerThanTwoLabels

class Rca(SemiSupervisedProjection):

    def __init__(self, experiment):
        SemiSupervisedProjection.__init__(self, experiment)
        self.projection = metric_learn.rca.RCA(dim = self.num_components, pca_comps = 0.70)

    def setProjectionMatrix(self):
        self.projection_matrix = np.transpose(
                self.pipeline.named_steps['projection'].transformer())

    def fit(self, instances, visu = True):
        features, labels = self.generateInputParameters(instances)
        self.setBestParameters(instances)
        # Select the right number of PCA components
        pca_comps = 0.90
        nan_values = True
        while nan_values:
            self.projection = metric_learn.rca.RCA(dim = self.num_components, pca_comps = pca_comps)
            self.createPipeline()
            self.pipeline.fit(features, labels)
            self.setProjectionMatrix()
            nan_values = np.isnan(self.projection_matrix).any()
            pca_comps -= 0.10
        self.setNumComponents()
        if visu:
            self.printProjectionMatrixCSV(instances.getFeaturesNames())

    def getFittingInstances(self, instances):
        return instances

    # RCA can handle chunks with one one instance.
    # There is no need to remove the instances those family is too rare.
    def generateInputLabels(self, instances):
        if self.conf.families_supervision:
            labels = instances.families
        else:
            labels = instances.labels
        ## String labels are transformed into integer labels (0 -> num_labels-1).
        ## This format is required by the library metric-learn.
        ## None labels are transformed into -1.
        labels_values = list(set(labels).difference(set([None])))
        if len(labels_values) < 2:
            raise FewerThanTwoLabels()
        labels = [labels_values.index(x) if x is not None else -1 for x in labels]
        return labels, instances
