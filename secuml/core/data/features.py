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


class StreamingUnsupported(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class FeaturesInfo(object):

    def __init__(self, ids, names, descriptions, types):
        self.ids = ids
        self.names = names
        self.descriptions = descriptions
        self.types = types
        self._check_validity()

    def num_features(self):
        return len(self.ids)

    def union(self, info):
        self.ids.extend(info.ids)
        self.names.extend(info.names)
        self.descriptions.extend(info.descriptions)
        self.types.extend(info.types)
        self._check_validity()

    def to_json(self):
        return {'ids': self.ids,
                'names': self.names,
                'descriptions': self.descriptions,
                'types': [type_.name for type_ in self.types]}

    @staticmethod
    def from_json(obj):
        return FeaturesInfo(obj['ids'], obj['names'], obj['descriptions'],
                            [FeatureType[type_] for type_ in obj['types']])

    def _check_validity(self):
        num_features = len(self.ids)
        if len(self.names) != num_features:
            raise InvalidFeatures('There are %d features ids '
                                  'but %d features names are provided.'
                                  % (num_features, len(self.names)))
        if len(self.descriptions) != num_features:
            raise InvalidFeatures('There are %d features ids '
                                  'but %d features descriptions are '
                                  'provided.' % (num_features,
                                                 len(self.descriptions)))
        if len(self.types) != num_features:
            raise InvalidFeatures('There are %d features ids '
                                  'but %d features types are provided.'
                                  % (num_features, len(self.types)))
        for type_ in self.types:
            if not isinstance(type_, FeatureType):
                raise InvalidFeatures(
                            'Features types must be an enum of FeatureType. '
                            '%s is not a valid value.' % str(type_))


class Features(object):

    # When streaming=True, values is an iterator where each element corresponds
    # the features of an instance.
    # Otherwise, values is a matrix containing the features of all the
    # instances (num rows = num instances, nu columns = num features).
    def __init__(self, values, info, instance_ids, streaming=False,
                 stream_batch=None):
        self.values = values
        self.info = info
        self.instance_ids = instance_ids
        self.streaming = streaming
        self.stream_batch = stream_batch
        self._check_validity()

    def _check_validity(self):
        if self.streaming:
            return
        num_instances = self.instance_ids.num_instances()
        if num_instances != 0:
            if self.values.shape[0] != num_instances:
                raise InvalidFeatures('There are %d instances '
                                      'but the features of %d are provided.'
                                      % (num_instances, self.values.shape[0]))
            num_features = self.info.num_features()
            if self.values.shape[1] != num_features:
                raise InvalidFeatures('There are %d features ids '
                                      'but the features of %d are provided.'
                                      % (num_features, self.values.shape[1]))
        else:
            if self.values.size != 0:
                raise InvalidFeatures('There is 0 instance but some features '
                                      'are provided.')

    def union(self, features):
        if self.streaming or features.streaming:
            raise StreamingUnsupported('Union is not supported for streaming '
                                       'features.')
        if features.get_values().shape[0] == 0:
            return
        if self.get_values().shape[0] == 0:
            self.values = features.values
        else:
            self.values = np.vstack((self.values, features.values))
        self._check_validity()

    def all_positives(self):
        if self.streaming:
            raise StreamingUnsupported('all_positives is not supported for '
                                       'streaming features.')
        return np.all(self.values >= 0)

    def get_from_ids(self, instance_ids):
        if self.streaming:
            raise StreamingUnsupported('get_from_ids is not supported for '
                                       'streaming features.')
        values = np.array([self.get_instance_features(i)
                           for i in instance_ids.ids])
        return Features(values, self.info, instance_ids)

    def get_names(self):
        return self.info.names

    def get_descriptions(self):
        return self.info.descriptions

    def get_ids(self):
        return self.info.ids

    def get_values(self):
        return self.values

    def num_features(self):
        return self.info.num_features()

    def set_instance_features(self, instance_id, features):
        if self.streaming:
            raise StreamingUnsupported('set_instance_features is not '
                                       'supported for streaming features.')
        index = self.instance_ids.get_index(instance_id)
        self.values[index] = features

    def get_instance_features(self, instance_id):
        if self.streaming:
            raise StreamingUnsupported('get_instance_features is not '
                                       'supported for streaming features.')
        index = self.instance_ids.get_index(instance_id)
        return self.values[index]

    def get_values_from_index(self, feature_index):
        if self.streaming:
            raise StreamingUnsupported('get_values_from_index is not '
                                       'supported for streaming features.')
        if self.instance_ids.num_instances() == 0:
            return []
        else:
            return self.values[:, feature_index]
