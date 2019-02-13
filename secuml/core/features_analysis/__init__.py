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

import json
import os.path as path

from .plots import FeaturePlots
from .scores import FeaturesScoring


class FeaturesAnalysis(object):

    def __init__(self, instances):
        self.instances = instances
        self.instances.features.set_types()
        self.num_features = self.instances.num_features()

    def compute(self):
        self._gen_features_plots()
        self._gen_features_scoring()

    def export(self, output_dir):
        self._export_features_types(output_dir)
        for feature_index in range(self.num_features):
            self.plots[feature_index].export(output_dir)
        self.scoring.export(output_dir)

    def _export_features_types(self, output_dir):
        features_types = {}
        features = self.instances.features
        for i in range(self.num_features):
            features_types[features.ids[i]] = features.types[i].name
        with open(path.join(output_dir, 'features_types.json'), 'w') as f:
            json.dump(features_types, f, indent=2)

    def _gen_features_plots(self):
        self.plots = [None] * self.num_features
        for feature_index in range(self.num_features):
            self.plots[feature_index] = FeaturePlots(self.instances,
                                                     feature_index)
            self.plots[feature_index].compute()

    def _gen_features_scoring(self):
        self.scoring = FeaturesScoring(self.instances)
        self.scoring.compute()
