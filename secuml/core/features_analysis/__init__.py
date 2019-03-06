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

from .plots import FeaturePlots
from .scores import FeaturesScoring


class FeaturesAnalysis(object):

    def __init__(self, instances):
        self.instances = instances
        self.num_features = self.instances.num_features()

    def compute(self):
        self._gen_features_plots()
        self._gen_features_scoring()

    def export(self, output_dir):
        for feature_index in range(self.num_features):
            self.plots[feature_index].export(output_dir)
        self.scoring.export(output_dir)

    def _gen_features_plots(self):
        self.plots = [None for _ in range(self.num_features)]
        for feature_index in range(self.num_features):
            self.plots[feature_index] = FeaturePlots(self.instances,
                                                     feature_index)
            self.plots[feature_index].compute()

    def _gen_features_scoring(self):
        self.scoring = FeaturesScoring(self.instances)
        self.scoring.compute()
