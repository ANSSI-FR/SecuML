## SecuML
## Copyright (C) 2016  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

from sklearn import discriminant_analysis

from SemiSupervisedProjection import SemiSupervisedProjection

class Lda(SemiSupervisedProjection):

    def __init__(self, experiment):
        SemiSupervisedProjection.__init__(self, experiment)
        self.projection = discriminant_analysis.LinearDiscriminantAnalysis(
                n_components = self.num_components)
        if not self.experiment.conf.sublabels_supervision:
            message  = 'WARNING: Lda projection without sublabels supervision. '
            message += 'The projection space is of dimension 1, and so the projected instances cannot be displayed '
            message += 'with hexagonal binnnings.'
            print message

    def setProjectionMatrix(self):
        self.projection_matrix = self.projection.scalings_

    def setNumComponents(self, num_components = None):
        num_classes = len(self.projection.classes_)
        if self.num_components is None:
            self.num_components = num_classes - 1
        else:
            self.num_components = min(num_classes - 1, self.num_components)
