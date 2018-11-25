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

import numpy as np
from sklearn.metrics import pairwise_distances


class ClassSeparation(object):

    def __init__(self, projection):
        self.projection = projection
        self.class_separation = None

    def computePerformance(self, instances):
        X = instances.features.getValues()
        labels = instances.ground_truth.getLabels()
        # For unsupervised projection methods, the performance is always computed with the labels (not the families).
        if hasattr(self.projection.conf, 'families_supervision'):
            if self.projection.conf.families_supervision:
                labels = instances.ground_truth.getFamilies()
        unique_labels, label_inds = np.unique(labels, return_inverse=True)
        ratio = 0
        for li in range(len(unique_labels)):
            Xc = X[label_inds == li]
            Xnc = X[label_inds != li]
            ratio += pairwise_distances(Xc).mean() / \
                pairwise_distances(Xc, Xnc).mean()
        self.class_separation = ratio / len(unique_labels)
