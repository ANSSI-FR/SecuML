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

from SecuML.core.clustering.Cluster import Cluster
from SecuML.exp.data import annotations_db_tools


class ClusterExp(Cluster):

    @staticmethod
    def from_json(obj):
        cluster = ClusterExp()
        cluster.instances_ids = obj['instances_ids']
        cluster.distances = obj['distances']
        cluster.label = obj['label']
        return cluster

    def get_labels_families(self, exp):
        annotations_type = exp.exp_conf.annotations_conf.annotations_type
        annotations_id = exp.exp_conf.annotations_conf.annotations_id
        dataset_id = exp.exp_conf.dataset_conf.dataset_id
        return annotations_db_tools.get_labels_families(exp.session,
                                                annotations_type,
                                                annotations_id, dataset_id,
                                                instance_ids=self.instances_ids)

    def get_label_family_ids(self, exp, label, family):
        annotations_type = exp.exp_conf.annotations_conf.annotations_type
        annotations_id = exp.exp_conf.annotations_conf.annotations_id
        dataset_id = exp.exp_conf.dataset_conf.dataset_id
        if label == 'unlabeled':
            return annotations_db_tools.getUnlabeledIds(exp.session,
                                                        annotations_type,
                                                        annotations_id,
                                                        self.instances_ids)
        else:
            return annotations_db_tools.get_label_family_ids(exp.session,
                                               annotations_type, annotations_id,
                                               dataset_id, label, family,
                                               instance_ids=self.instances_ids)
