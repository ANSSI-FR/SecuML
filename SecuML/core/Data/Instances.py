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

from .Annotations import Annotations
from .Features import Features
from .Ids import Ids


class Instances(object):

    def __init__(self, ids, features, features_names, features_descriptions,
                 labels, families, ground_truth_labels, ground_truth_families,
                 idents=None, timestamps=None):
        self.ids = Ids(ids, idents=idents, timestamps=timestamps)
        self.features = Features(features, features_names,
                                 features_descriptions, self.ids)
        self.annotations = Annotations(labels, families, self.ids)
        self.ground_truth = Annotations(ground_truth_labels,
                                        ground_truth_families,
                                        self.ids)

    # The union must be used on instances coming from the same dataset.
    # Otherwise, there may be some collisions on the ids.
    def union(self, instances):
        if instances.numInstances() == 0:
            return
        self.ids.union(instances.ids)
        self.features.union(instances.features)
        self.annotations.union(instances.annotations)
        self.ground_truth.union(instances.ground_truth)

    def hasGroundTruth(self):
        return all(l is not None for l in self.ground_truth.getLabels())

    def getAnnotations(self, ground_truth):
        if ground_truth:
            return self.ground_truth
        else:
            return self.annotations

    def numInstances(self, label='all', ground_truth=False):
        annotations = self.getAnnotations(ground_truth)
        return annotations.numInstances(label=label)

    def eraseAnnotations(self):
        self.annotations.erase()

    def getUnlabeledInstances(self):
        instance_ids = self.annotations.getUnlabeledIds()
        return self.getInstancesFromIds(instance_ids)

    def getAnnotatedInstances(self, label='all'):
        instance_ids = self.annotations.getAnnotatedIds(label=label)
        return self.getInstancesFromIds(instance_ids)

    def getInstancesFromIds(self, instance_ids):
        features = self.features.getInstancesFromIds(instance_ids)
        idents, timestamps = self.ids.getIdentsTimestampsFromIds(instance_ids)
        labels, families = self.annotations.getAnnotationsFromIds(instance_ids)
        gt_labels, gt_families = self.ground_truth.getAnnotationsFromIds(
                instance_ids)
        selected_instances = Instances(instance_ids, features, self.features.getNames(),
                                       self.features.getDescriptions(),
                                       labels, families,
                                       gt_labels, gt_families,
                                       idents=idents, timestamps=timestamps)
        return selected_instances
