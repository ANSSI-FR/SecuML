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

import numpy as np

from secuml.core.data.labels_tools import label_str_to_bool
from secuml.core.tools.core_exceptions import SecuMLcoreException


class InvalidAnnotations(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Annotations(object):

    def __init__(self, labels, families, ids):
        self.ids = ids
        self._set_labels_families(labels, families)
        self.check_validity()

    def check_validity(self):
        num_instances = self.ids.num_instances()
        if self.labels.shape[0] != num_instances:
            raise InvalidAnnotations('There are %d instances '
                                     'but %d labels are provided.'
                                     % (num_instances, self.labels.shape[0]))
        elif self.families.shape[0] != num_instances:
            raise InvalidAnnotations('There are %d instances '
                                     'but %d families are provided.'
                                     % (num_instances, self.families.shape[0]))

    def _set_labels_families(self, labels, families):
        self.set_labels(labels)
        self.set_families(families)

    # The union must be used on instances coming from the same dataset.
    # Otherwise, there may be some collisions on the ids.
    def union(self, annotations):
        self.labels = np.hstack((self.labels, annotations.labels))
        self.families = np.hstack((self.families, annotations.families))
        self.check_validity()

    def get_from_ids(self, ids):
        if ids.num_instances() == 0:
            return Annotations(None, None, ids)
        else:
            indexes = np.array([self.ids.get_index(i) for i in ids.ids])
            return Annotations(self.labels[indexes], self.families[indexes],
                               ids)

    def get_from_indices(self, ids, indices):
        if ids.num_instances() == 0:
            return Annotations(None, None, ids)
        else:
            return Annotations(self.labels[indices], self.families[indices],
                               ids)

    def num_instances(self, label='all'):
        if label == 'all':
            return self.ids.num_instances()
        else:
            return len(self.get_annotated_ids(label=label))

    def get_supervision(self, multiclass):
        if multiclass:
            return self.get_families()
        else:
            return self.get_labels()

    def get_labels(self):
        return self.labels

    def get_label(self, instance_id):
        return self.labels[self.ids.get_index(instance_id)]

    def set_label(self, instance_id, label):
        self.labels[self.ids.get_index(instance_id)] = label

    def set_labels(self, labels):
        num_instances = self.ids.num_instances()
        if labels is None:
            labels = np.full((num_instances,), None)
        elif labels.shape[0] != num_instances:
            raise InvalidAnnotations('There are %d instances '
                                     'but there %d labels are provided.'
                                     % (num_instances, len(labels)))
        self.labels = labels

    def get_families(self):
        return self.families

    def get_family(self, instance_id):
        return self.families[self.ids.get_index(instance_id)]

    def set_family(self, instance_id, family):
        self.families[self.ids.get_index(instance_id)] = family

    def set_label_family(self, instance_id, label, family):
        index = self.ids.get_index(instance_id)
        self.labels[index] = label
        self.families[index] = family

    def get_label_family(self, instance_id):
        index = self.ids.get_index(instance_id)
        return self.labels[index], self.families[index]

    def set_families(self, families):
        num_instances = self.ids.num_instances()
        if families is None:
            families = np.full((num_instances,), None)
        elif families.shape[0] != num_instances:
            raise InvalidAnnotations('There are %d instances '
                                     'but %d families are provided.'
                                     % (num_instances, len(families)))
        self.families = families

    def get_family_ids(self, family):
        return self.ids.ids[self.families == family]

    def get_families_values(self, label='all'):
        families = self.families
        if label != 'all':
            families = self.families[self.labels == label_str_to_bool(label)]
        return set(families[families != None])  # NOQA: 711

    def get_families_count(self, label='all'):
        families_values = self.get_families_values(label=label)
        families_count = {}
        for family in families_values:
            families_count[family] = len(self.get_family_ids(family))
        return families_count

    def get_families_prop(self, label='all'):
        families_prop = self.get_families_count(label=label)
        for family in list(families_prop.keys()):
            families_prop[family] /= self.num_instances(label=label)
        return families_prop

    def get_annotated_ids(self, label='all', family=None):
        if label == 'all':
            mask = self.labels != None  # NOQA: 711
        else:
            mask = self.labels == label_str_to_bool(label)
        if family is not None:
            family_mask = self.families == family
            mask = np.logical_and(mask, family_mask)
        return self.ids.ids[mask]

    def get_unlabeled_ids(self):
        return self.ids.ids[self.labels == None]  # NOQA: 711

    def has_unlabeled_ids(self):
        for i in self.ids.get_ids():
            if not self.is_annotated(i):
                return True
        return False

    def is_annotated(self, instance_id):
        return self.get_label(instance_id) is not None
