# SecuML
# Copyright (C) 2018 ANSSI
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

from SecuML.core.Clustering.Cluster import Cluster
from SecuML.experiments.Data import annotations_db_tools


class ClusterExp(Cluster):

    @staticmethod
    def fromJson(obj):
        cluster = ClusterExp()
        cluster.instances_ids = obj['instances_ids']
        cluster.distances = obj['distances']
        cluster.label = obj['label']
        return cluster

    def getClusterLabelsFamilies(self, experiment):
        labels_family = annotations_db_tools.getLabelsFamilies(
            experiment.session,
            experiment.experiment_id,
            instance_ids=self.instances_ids)
        return labels_family

    def getClusterLabelFamilyIds(self, experiment, label, family):
        if label == 'unknown' and (family is None or family == 'unknown'):
            ids = annotations_db_tools.getUnlabeledIds(
                experiment.session,
                experiment.experiment_id,
                instance_ids=self.instances_ids)
        else:
            ids = annotations_db_tools.getLabelFamilyIds(
                experiment.session,
                experiment.experiment_id,
                label, family,
                instance_ids=self.instances_ids)
        return ids
