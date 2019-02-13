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

from secuml.core.projection.projection import Projection


class UnsupervisedProjection(Projection):

    @abc.abstractmethod
    def set_projection_matrix(self):
        return

    def gen_input_params(self, instances):
        return self.features_preprocessing(instances)

    def fit(self, instances):
        features = self.gen_input_params(instances)
        self.create_pipeline()
        self.pipeline.fit(features)
        self.set_projection_matrix()
        self.set_num_components()
