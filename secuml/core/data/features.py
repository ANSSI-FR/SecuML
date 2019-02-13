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

from enum import Enum
import numpy as np

from secuml.core.tools.core_exceptions import SecuMLcoreException


class FeatureType(Enum):
    binary = 0
    numeric = 1


class InvalidFeatures(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Features(object):

    def __init__(self, values, ids, names, descriptions, instance_ids):
        self.instance_ids = instance_ids
        self.values = np.array(values)
        self.ids = ids
        self.names = names
        self.descriptions = descriptions
        self.check_validity()

    def check_validity(self):
        num_instances = self.instance_ids.num_instances()
        if num_instances != 0:
            num_features = self.values.shape[1]
            if self.values.shape[0] != num_instances:
                raise InvalidFeatures('There are %d instances '
                                      'but the features of %d are provided.'
                                      % (num_instances, self.values.shape[0]))
            elif len(self.names) != num_features:
                raise InvalidFeatures('There are %d features '
                                      'but %d features names are provided.'
                                      % (num_features, len(self.names)))
            elif len(self.descriptions) != num_features:
                raise InvalidFeatures('There are %d features '
                                      'but %d features descriptions are '
                                      'provided.' % (num_features,
                                                     len(self.descriptions)))
        else:
            if self.values.size != 0:
                raise InvalidFeatures('There is 0 instance but some features '
                                      'are provided.')

    def union(self, features):
        if features.get_values().shape[0] == 0:
            return
        if self.get_values().shape[0] == 0:
            self.values = features.values
        else:
            self.values = np.vstack((self.values, features.values))
        self.check_validity()

    def set_types(self):
        self.types = [None] * self.num_features()
        for i in range(self.num_features()):
            values = self.get_values_from_index(i)
            if all(v in [0, 1] for v in values):
                self.types[i] = FeatureType.binary
            else:
                self.types[i] = FeatureType.numeric

    def all_positives(self):
        return np.all(self.values >= 0)

    def get_from_ids(self, instance_ids):
        values = [self.get_instance_features(i) for i in instance_ids.ids]
        return Features(values, self.ids, self.names, self.descriptions,
                        instance_ids)

    def get_names(self):
        return self.names

    def get_descriptions(self):
        return self.descriptions

    def get_ids(self):
        return self.ids

    def get_values(self):
        return self.values

    def num_features(self):
        return len(self.ids)

    def set_instance_features(self, instance_id, features):
        index = self.instance_ids.get_index(instance_id)
        self.values[index] = features

    def get_instance_features(self, instance_id):
        index = self.instance_ids.get_index(instance_id)
        return self.values[index]

    def get_values_from_index(self, feature_index):
        return [self.values[i][feature_index]
                for i in range(self.instance_ids.num_instances())]
