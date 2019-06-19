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

from secuml.core.data import labels_tools
from secuml.core.data.labels_tools import BENIGN, MALICIOUS
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
        if len(self.labels) != num_instances:
            raise InvalidAnnotations('There are %d instances '
                                     'but %d labels are provided.'
                                     % (num_instances,
                                        len(self.labels)))
        elif len(self.families) != num_instances:
            raise InvalidAnnotations('There are %d instances '
                                     'but %d families are provided.'
                                     % (num_instances,
                                        len(self.families)))

    def _set_labels_families(self, labels, families):
        if labels is None:
            labels = [None for _ in range(self.ids.num_instances())]
        if families is None:
            families = [None for _ in range(self.ids.num_instances())]
        self.set_labels(labels)
        self.set_families(families)

    # The union must be used on instances coming from the same dataset.
    # Otherwise, there may be some collisions on the ids.
    def union(self, annotations):
        self.labels = self.labels + annotations.labels
        self.families = self.families + annotations.families
        self.check_validity()

    def get_from_ids(self, ids):
        return Annotations([self.get_label(i) for i in ids.ids],
                           [self.get_family(i) for i in ids.ids],
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
        if len(labels) != num_instances:
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
        if len(families) != num_instances:
            raise InvalidAnnotations('There are %d instances '
                                     'but %d families are provided.'
                                     % (num_instances,
                                        len(families)))
        self.families = families

    def get_family_ids(self, family):
        return [i for i in self.ids.get_ids() if self.get_family(i) == family]

    def get_families_values(self, label='all'):
        if label == 'all':
            indexes = range(self.ids.num_instances())
        else:
            label_b = labels_tools.label_str_to_bool(label)
            indexes = [i for i in range(self.ids.num_instances())
                       if self.labels[i] is not None
                       and self.labels[i] == label_b]
        families = set([self.families[i]
                        for i in indexes if self.families[i] is not None])
        return families

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
        annotated_ids = [i for i in self.ids.get_ids() if self.is_annotated(i)]
        if label == MALICIOUS:
            annotated_ids = [i for i in annotated_ids if self.get_label(i)]
        elif label == BENIGN:
            annotated_ids = [i for i in annotated_ids if not self.get_label(i)]
        if family is not None:
            return [i for i in annotated_ids if self.get_family(i) == family]
        else:
            return annotated_ids

    def get_unlabeled_ids(self):
        return [i for i in self.ids.get_ids() if not self.is_annotated(i)]

    def has_unlabeled_ids(self):
        for i in self.ids.get_ids():
            if not self.is_annotated(i):
                return True
        return False

    def is_annotated(self, instance_id):
        return self.get_label(instance_id) is not None
