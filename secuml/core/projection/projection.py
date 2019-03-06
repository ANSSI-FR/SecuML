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
import copy
import numpy as np
import os.path as path
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from secuml.core.data.features import Features
from secuml.core.data.features import FeaturesInfo
from secuml.core.data.features import FeatureType
from secuml.core.data.instances import Instances
from .monitoring.perf import PerfMonitoring
from .monitoring.visu import Visualization


class Projection(object):

    def __init__(self, conf):
        self.conf = conf

    @abc.abstractmethod
    def gen_input_params(self, instances):
        return

    def component_labels(self, features_names):
        return ['C_' + str(x) for x in range(self.num_components)]

    def set_num_components(self):
        self.num_components = self.projection_matrix.shape[1]

    def create_pipeline(self):
        self.pipeline = Pipeline([('scaler', StandardScaler()),
                                  ('projection', self.projection)])

    @abc.abstractmethod
    def set_projection_matrix(self):
        return

    @abc.abstractmethod
    def fit(self, instances):
        return

    def transform(self, instances):
        features_values = instances.features.get_values()
        features_names = instances.features.get_names()
        projected_features = self.component_labels(features_names)
        projection_types = [FeatureType.numeric
                            for _ in range(self.num_components)]
        projection = Features(self.pipeline.transform(features_values),
                              FeaturesInfo(range(len(projected_features)),
                                           projected_features,
                                           projected_features,
                                           projection_types),
                              instances.ids)
        return Instances(instances.ids, projection, instances.annotations,
                         instances.ground_truth)

    def features_preprocessing(self, instances):
        features = copy.deepcopy(instances.features.get_values())
        features = np.array(features)
        features.flat[::features.shape[1] + 1] += 0.01
        return features

    def export_fit(self, output_dir, instances):
        self.export_projection_matrix(output_dir, instances.features.get_names())

    def export_transform(self, output_dir, instances, projected_instances):
        visu = Visualization(self, output_dir)
        visu.all_hex_bin(projected_instances)
        self.assess_perf(output_dir, projected_instances)

    def assess_perf(self, output_dir, projected_instances):
        if not projected_instances.has_ground_truth():
            return None
        evaluation = PerfMonitoring(self)
        evaluation.computer_perf(projected_instances)
        return evaluation

    def export_projection_matrix(self, output_dir, features_names):
        projection_matrix = pd.DataFrame(
                                 self.projection_matrix,
                                 columns=self.component_labels(features_names),
                                 index=features_names)
        projection_matrix.index.name = 'feature'
        projection_matrix.to_csv(path.join(output_dir, 'projection_matrix.csv'),
                                 sep=',',
                                 header=True,
                                 index=True)
