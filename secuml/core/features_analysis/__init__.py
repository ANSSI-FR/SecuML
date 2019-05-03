# SecuML
# Copyright (C) 2016-2019  ANSSI
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

    def __init__(self, instances, with_density=True):
        self.instances = instances
        self.with_density = with_density
        self.num_features = self.instances.num_features()
        self.plots = []
        self.scoring = FeaturesScoring(self.instances)

    def gen_plots(self, output_dir, save=False):
        for feature_index in range(self.num_features):
            plot = FeaturePlots(self.instances, feature_index,
                                with_density=self.with_density)
            plot.compute()
            plot.export(output_dir)
            if save:
                self.plots.append(plot)

    def gen_scoring(self, output_dir):
        self.scoring.compute()
        self.scoring.export(output_dir)
