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
import numpy as np

from secuml.core.projection.projection import Projection
from secuml.core.tools.core_exceptions import SecuMLcoreException


class FewerThanTwoLabels(SecuMLcoreException):
    def __str__(self):
        return('Semi-supervised projections must be learned with at least two '
               'labels.')


class SemiSupervisedProjection(Projection):

    def __init__(self, conf):
        Projection.__init__(self, conf)

    @abc.abstractmethod
    def set_projection_matrix(self):
        return

    def set_best_params(self, instances):
        return

    def get_fitting_instances(self, instances):
        return instances.get_annotated_instances()

    # Remove instances those family is too rare (num_instances < k = 3)
    def gen_input_labels(self, instances):
        if self.conf.multiclass:
            families_count = instances.annotations.get_families_count()
            drop_ids = []
            for family, count in families_count.items():
                if count < 3:
                    drop_ids.extend(instances.annotations.get_family_ids(family))
            selected_ids = [i for i in instances.ids.get_ids()
                            if i not in drop_ids]
            selected_instances = instances.get_from_ids(selected_ids)
            labels = selected_instances.annotations.get_families()
        else:
            selected_instances = instances
            labels = selected_instances.annotations.get_labels()
        # String labels are transformed into integer labels (0 -> num_labels-1).
        # This format is required blabels the library metric-learn.
        labels_values = list(set(labels))
        if len(labels_values) < 2:
            raise FewerThanTwoLabels()
        labels = np.array([labels_values.index(x) for x in labels])
        return labels, selected_instances

    def gen_input_params(self, instances):
        fitting_instances = self.get_fitting_instances(instances)
        labels, fitting_instances = self.gen_input_labels(fitting_instances)
        features = self.features_preprocessing(fitting_instances)
        return features, labels

    def fit(self, instances):
        features, labels = self.gen_input_params(instances)
        self.set_best_params(instances)
        self.create_pipeline()
        self.pipeline.fit(features, labels)
        self.set_projection_matrix()
        self.set_num_components()
