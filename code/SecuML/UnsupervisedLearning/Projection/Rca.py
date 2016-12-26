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
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

import copy
import metric_learn
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from SemiSupervisedProjection import SemiSupervisedProjection

class Rca(SemiSupervisedProjection):

    def __init__(self, experiment):
        SemiSupervisedProjection.__init__(self, experiment)
        self.projection = metric_learn.rca.RCA(dim = self.num_components)
    
    def run(self, instances, quick = False):
        self.fit(instances, quick = quick)
        self.transform(instances, quick = quick)
    
    # Remove instances those sublabel is too rare (num_instances < k = 3)
    def fit(self, instances, quick = False):
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('projection', self.projection)])
        if self.experiment.conf.sublabels_supervision:
            sublabels_count = instances.getSublabelsCount()
            drop_ids = []
            for sublabel, count in sublabels_count.iteritems():
                if count < 3:
                    drop_ids += instances.getSublabelIds(sublabel)
            selected_ids = [i for i in instances.getIds() if i not in drop_ids]
            instances = instances.getInstancesFromIds(selected_ids)
            y = instances.sublabels
        else:
            y = instances.labels
        labels_values = list(set(y).difference(set([None])))
        if len(labels_values) < 2:
            raise FewerThanTwoLabels()
        ## String labels are transformed into integer labels (0 -> num_labels-1)
        ## This format is required by the library metric-learn
        ## None labels are transformed into -1
        y = [labels_values.index(x) if x is not None else -1 for x in y]
        instances_np = copy.deepcopy(instances.getFeatures())
        instances_np = np.array(instances_np)
        instances_np.flat[::instances_np.shape[1] + 1] += 0.01
        self.pipeline.fit(instances_np, y)
        self.setNumComponents(instances.numFeatures())
        self.setProjectionMatrix()
        if not quick:
            self.printProjectionMatrixCSV(instances.getFeaturesNames())

    def setProjectionMatrix(self):
        self.projection_matrix = np.transpose(
                self.pipeline.named_steps['projection'].transformer())

    def setNumComponents(self, num_components):
        if self.num_components is None:
            self.num_components = num_components
        return
