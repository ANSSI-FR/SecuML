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
# with SecuML. If not, see <http://www.gnu.org/licenses/>.

from sklearn.feature_selection import RFE

from .SemiSupervisedFeatureSelection import SemiSupervisedFeatureSelection


class RecursiveFeatureElimination(SemiSupervisedFeatureSelection):

    def __init__(self, conf):
        SemiSupervisedFeatureSelection.__init__(self, conf)
        self.projection = RFE(estimator=conf.model,
                              n_features_to_select=conf.num_components,
                              step=conf.step)
