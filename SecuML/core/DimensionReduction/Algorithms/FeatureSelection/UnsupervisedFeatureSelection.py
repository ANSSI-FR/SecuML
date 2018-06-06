# SecuML
# Copyright (C) 2017  ANSSI
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
from sklearn.pipeline import Pipeline

from SecuML.core.DimensionReduction.FeatureSelection import FeatureSelection


class UnsupervisedFeatureSelection(FeatureSelection):

    def __init__(self, conf):
        FeatureSelection.__init__(self, conf)

    def generateInputParameters(self, instances):
        return self.featuresPreprocessing(instances)

    def fit(self, instances):
        features = self.generateInputParameters(instances)
        self.createPipeline()
        self.pipeline.fit(features)
        self.setProjectionMatrix()

    def createPipeline(self):
        self.pipeline = Pipeline([
            ('projection', self.projection)])

    def getSelectedFeatures(self, features_names):
        selected_features = list(np.array(features_names)[
                                 self.projection.get_support()])
        return selected_features

    # The name of the selected features.
    def componentLabels(self, features_names):
        return self.getSelectedFeatures(features_names)
