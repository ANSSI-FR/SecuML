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

from secuml.core.data import labels_tools
from secuml.core.data.labels_tools import BENIGN, MALICIOUS


class Datasets(object):

    def __init__(self, instances):
        self.instances = instances
        self.init_counts()

    def update(self, instance_id, label, family):
        self.new_annotations = True
        self.instances.annotations.set_label_family(
                                       instance_id,
                                       labels_tools.label_str_to_bool(label),
                                       family)
        # Update the annotation count
        self.num_annotations[label] += 1

    def num_annotations(self, label='all'):
        return len(self.instances.annotations.get_annotated_ids(label=label))

    def get_unlabeled_instances(self):
        return self.instances.get_unlabeled_instances()

    def init_counts(self):
        self.ground_truth = {}
        self.num_init = {}
        self.num_annotations = {}
        for label in [MALICIOUS, BENIGN]:
            self.ground_truth[label] = None
            if self.instances.has_ground_truth():
                num = self.instances.num_instances(label=label,
                                                   ground_truth=True)
                self.ground_truth[label] = num
            self.num_init[label] = self.instances.get_annotated_instances(
                    label=label).num_instances()
            self.num_annotations[label] = self.num_init[label]
