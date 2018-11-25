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

from SecuML.core.data import labels_tools
from SecuML.core.tools.core_exceptions import SecuMLcoreException


class InvalidAnnotations(SecuMLcoreException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Annotations(object):

    def __init__(self, labels, families, ids):
        self.ids = ids
        self.labels = labels
        self.families = families
        self.checkValidity()

    def checkValidity(self):
        num_instances = self.ids.numInstances()
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

    # The union must be used on instances coming from the same dataset.
    # Otherwise, there may be some collisions on the ids.
    def union(self, annotations):
        self.labels = self.labels + annotations.labels
        self.families = self.families + annotations.families
        self.checkValidity()

    def getAnnotationsFromIds(self, instance_ids):
        labels = [self.getLabel(i) for i in instance_ids]
        families = [self.getFamily(i) for i in instance_ids]
        return labels, families

    def numInstances(self, label='all'):
        if label == 'all':
            return self.ids.numInstances()
        else:
            return len(self.getAnnotatedIds(label=label))

    def getSupervision(self, families_supervision):
        if families_supervision:
            return self.getFamilies()
        else:
            return self.getLabels()

    def getLabels(self):
        return self.labels

    def getLabel(self, instance_id):
        index = self.ids.getIndex(instance_id)
        return self.labels[index]

    def setLabel(self, instance_id, label):
        index = self.ids.getIndex(instance_id)
        self.labels[index] = label

    def setLabels(self, labels):
        num_instances = self.ids.numInstances()
        if len(labels) != num_instances:
            raise InvalidAnnotations('There are %d instances '
                                     'but there %d labels are provided.'
                                     % (num_instances,
                                        len(labels)))
        self.labels = labels

    def getFamilies(self):
        return self.families

    def getFamily(self, instance_id):
        index = self.ids.getIndex(instance_id)
        return self.families[index]

    def setFamily(self, instance_id, family):
        index = self.ids.getIndex(instance_id)
        self.families[index] = family

    def setLabelFamily(self, instance_id, label, family):
        index = self.ids.getIndex(instance_id)
        self.labels[index] = label
        self.families[index] = family

    def getLabelFamily(self, instance_id):
        index = self.ids.getIndex(instance_id)
        return self.labels[index], self.families[index]

    def setFamilies(self, families):
        num_instances = self.ids.numInstances()
        if len(families) != num_instances:
            raise InvalidAnnotations('There are %d instances '
                                     'but %d families are provided.'
                                     % (num_instances,
                                        len(families)))
        self.families = families

    def getFamilyIds(self, family):
        return [i for i in self.ids.getIds() if self.getFamily(i) == family]

    def getFamiliesValues(self, label='all'):
        if label == 'all':
            indexes = range(self.ids.numInstances())
        else:
            l = labels_tools.labelStringToBoolean(label)
            indexes = [i for i in range(self.ids.numInstances()) if
                       self.labels[i] is not None and self.labels[i] == l]
        families = set([self.families[i]
                        for i in indexes if self.families[i] is not None])
        return families

    def getFamiliesCount(self, label='all'):
        families_values = self.getFamiliesValues(label=label)
        families_count = {}
        for family in families_values:
            families_count[family] = len(self.getFamilyIds(family))
        return families_count

    def getFamiliesProp(self, label='all'):
        families_prop = self.getFamiliesCount(label=label)
        for family in list(families_prop.keys()):
            families_prop[family] /= self.numInstances(label=label)
        return families_prop

    def getAnnotatedIds(self, label='all'):
        annotated_ids = [i for i in self.ids.getIds() if self.isAnnotated(i)]
        if label == 'all':
            return annotated_ids
        elif label == labels_tools.MALICIOUS:
            return [i for i in annotated_ids if self.getLabel(i)]
        elif label == labels_tools.BENIGN:
            return [i for i in annotated_ids if not self.getLabel(i)]

    def getUnlabeledIds(self):
        return [i for i in self.ids.getIds() if not self.isAnnotated(i)]

    def isAnnotated(self, instance_id):
        return self.getLabel(instance_id) is not None
