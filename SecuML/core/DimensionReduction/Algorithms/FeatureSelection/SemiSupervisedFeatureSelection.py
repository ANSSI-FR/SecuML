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

import numpy as np

from sklearn.feature_selection import VarianceThreshold
from sklearn.pipeline import Pipeline

from SecuML.core.DimensionReduction.FeatureSelection import FeatureSelection


class FewerThanTwoLabels(Exception):
    def __str__(self):
        return ('Semi-supervised projections must be learned with at least two labels.')


class SemiSupervisedFeatureSelection(FeatureSelection):

    def __init__(self, conf):
        FeatureSelection.__init__(self, conf)

    def setBestParameters(self, instances):
        return

    def getFittingInstances(self, instances):
        return instances.getAnnotatedInstances()

    # Remove instances those family is too rare (num_instances < k = 3)
    def generateInputLabels(self, instances):
        if self.conf.families_supervision:
            families_count = instances.getFamiliesCount()
            drop_ids = []
            for family, count in families_count.items():
                if count < 3:
                    drop_ids += instances.getFamilyIds(family)
            selected_ids = [i for i in instances.ids.getIds()
                            if i not in drop_ids]
            selected_instances = instances.getInstancesFromIds(selected_ids)
            labels = selected_instances.families
        else:
            selected_instances = instances
            labels = selected_instances.annotations.getLabels()
        # String labels are transformed into integer labels (0 -> num_labels-1).
        # This format is required blabels the library metric-learn.
        labels_values = list(set(labels))
        if len(labels_values) < 2:
            raise FewerThanTwoLabels()
        labels = np.array([labels_values.index(x) for x in labels])
        return labels, selected_instances

    def generateInputParameters(self, instances):
        fitting_instances = self.getFittingInstances(instances)
        labels, fitting_instances = self.generateInputLabels(fitting_instances)
        features = self.featuresPreprocessing(fitting_instances)
        return features, labels

    def fit(self, instances):
        features, labels = self.generateInputParameters(instances)
        self.setBestParameters(instances)
        self.createPipeline()
        self.pipeline.fit(features, labels)
        self.setProjectionMatrix()

    def createPipeline(self):
        # Remove features with null variance
        self.var_filter = VarianceThreshold()
        self.pipeline = Pipeline([
            ('var_filter', self.var_filter),
            ('projection', self.projection)])

    def getSelectedFeatures(self, features_names):
        non_constant_features = np.array(features_names)[
            self.var_filter.get_support()]
        selected_features = list(
            non_constant_features[self.projection.get_support()])
        return selected_features

    # The name of the selected features.
    def componentLabels(self, features_names):
        return self.getSelectedFeatures(features_names)
