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

from sklearn import discriminant_analysis

from .SemiSupervisedProjection import SemiSupervisedProjection


class Lda(SemiSupervisedProjection):

    def __init__(self, conf):
        SemiSupervisedProjection.__init__(self, conf)
        self.projection = discriminant_analysis.LinearDiscriminantAnalysis(
            n_components=conf.num_components)
        if not self.conf.families_supervision:
            self.conf.logger.warning(
                    'Lda projection without families supervision. '
                    'The projection space is of dimension 1, and so the '
                    'projected instances cannot be displayed with hexagonal '
                    'binnnings.')

    def setProjectionMatrix(self):
        self.projection_matrix = self.projection.scalings_

    def generateInputLabels(self, instances):
        labels, instances = SemiSupervisedProjection.generateInputLabels(
                                                              self,
                                                              instances)
        num_classes = len(set(labels))
        if (self.conf.num_components is not None and
                self.conf.num_components > num_classes - 1):
            self.conf.logger.warning(
                    'The embedding dimension must be smaller '
                    'than the number of classes - 1. '
                    'num_components is set to %d.' % (num_classes - 1))
            self.num_components = num_classes - 1
            self.projection = discriminant_analysis.LinearDiscriminantAnalysis(
                n_components=self.conf.num_components)
        return labels, instances
