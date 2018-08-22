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
# with SecuML. If not, see <http://www.gnu.org/licenses/>.

from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import SelectKBest

from .SemiSupervisedFeatureSelection import SemiSupervisedFeatureSelection


class MutualInfoClassif(SemiSupervisedFeatureSelection):

    def __init__(self, conf):
        SemiSupervisedFeatureSelection.__init__(self, conf)
        self.projection = SelectKBest(
            mutual_info_classif, k=conf.num_components)
