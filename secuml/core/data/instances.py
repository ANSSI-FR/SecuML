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


class Instances(object):

    def __init__(self, ids, features, annotations, ground_truth):
        self.ids = ids
        self.features = features
        self.annotations = annotations
        self.ground_truth = ground_truth

    # The union must be used on instances coming from the same dataset.
    # Otherwise, there may be some collisions on the ids.
    def union(self, instances):
        if instances.num_instances() == 0:
            return
        self.ids.union(instances.ids)
        self.features.union(instances.features)
        self.annotations.union(instances.annotations)
        self.ground_truth.union(instances.ground_truth)

    def has_ground_truth(self):
        return all(l is not None for l in self.ground_truth.get_labels())

    def get_annotations(self, ground_truth):
        if ground_truth:
            return self.ground_truth
        else:
            return self.annotations

    def num_instances(self, label='all', ground_truth=False):
        annotations = self.get_annotations(ground_truth)
        return annotations.num_instances(label=label)

    def num_features(self):
        return self.features.num_features()

    def get_unlabeled_instances(self):
        instance_ids = self.annotations.get_unlabeled_ids()
        return self.get_from_ids(instance_ids)

    def get_annotated_instances(self, label='all', family=None):
        instance_ids = self.annotations.get_annotated_ids(label=label,
                                                          family=family)
        return self.get_from_ids(instance_ids)

    def get_from_ids(self, instance_ids):
        ids = self.ids.get_from_ids(instance_ids)
        features = self.features.get_from_ids(ids)
        annotations = self.annotations.get_from_ids(ids)
        ground_truth = self.ground_truth.get_from_ids(ids)
        return Instances(ids, features, annotations, ground_truth)

    def get_features_ids(self):
        return self.features.get_ids()

    def get_sorted_timestamps(self):
        timestamps = self.ids.timestamps
        indexes = list(range(self.num_instances()))
        t_indexes = list(zip(timestamps, indexes))
        t_indexes.sort()
        t_start = t_indexes[0][0]
        t_end = t_indexes[-1][0]
        return t_indexes, t_start, t_end
