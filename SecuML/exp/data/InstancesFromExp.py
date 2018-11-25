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

from SecuML.core.data.Ids import Ids
from SecuML.core.data.Instances import Instances
from SecuML.core.data import labels_tools

from SecuML.exp import db_tables
from SecuML.exp.conf.AnnotationsConf import AnnotationsTypes
from SecuML.exp.data import annotations_db_tools

from .FeaturesFromExp import FeaturesFromExp


class InstancesFromExp(Instances):

    def __init__(self, experiment):
        self._set_exp_conf(experiment)
        ids = self.getIds()
        timestamps = self.getTimestamps()
        features_exp = FeaturesFromExp(experiment, Ids(ids))
        labels, families = self._getAnnotations()
        gt_labels, gt_families = self._getGroundTruth()
        Instances.__init__(self, ids, features_exp.values, features_exp.ids,
                           features_exp.names, features_exp.descriptions,
                           labels, families, gt_labels, gt_families,
                           timestamps=timestamps)

    def _set_exp_conf(self, experiment):
        self.experiment = experiment
        self.session = experiment.session
        self.exp_conf = experiment.exp_conf
        self.dataset_conf = experiment.exp_conf.dataset_conf
        self.annotations_conf = experiment.exp_conf.annotations_conf

    def getIds(self):
        ids = db_tables.getDatasetIds(self.session,
                                      self.dataset_conf.dataset_id)
        self.num_instances = len(ids)
        self.indexes = {}
        for i in range(len(ids)):
            self.indexes[ids[i]] = i
        return ids

    def getTimestamps(self):
        return db_tables.getDatasetTimestamps(self.session,
                                              self.dataset_conf.dataset_id)

    def _getAnnotations(self):
        annotations_type = self.annotations_conf.annotations_type
        if annotations_type == AnnotationsTypes.none:
            labels = [None] * self.num_instances
            families = [None] * self.num_instances
            return labels, families
        if annotations_type == AnnotationsTypes.ground_truth:
            return self._getGroundTruth()
        if annotations_type == AnnotationsTypes.partial:
            labels = [None] * self.num_instances
            families = [None] * self.num_instances
            annotations = annotations_db_tools.getAnnotatedInstances(
                    self.session, self.annotations_conf.annotations_id)
            for instance_id, label, family in annotations:
                index = self.indexes[instance_id]
                labels[index] = labels_tools.labelStringToBoolean(label)
                families[index] = family
            return labels, families

    def _getGroundTruth(self):
        if not self.dataset_conf.has_ground_truth:
            labels = [None] * self.num_instances
            families = [None] * self.num_instances
            return labels, families
        dataset_id = self.dataset_conf.dataset_id
        return annotations_db_tools.getGroundTruth(self.session, dataset_id)
