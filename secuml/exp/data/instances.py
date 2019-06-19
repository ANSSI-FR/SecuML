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

from secuml.core.data.annotations import Annotations
from secuml.core.data.ids import Ids
from secuml.core.data.instances import Instances as CoreInstances
from secuml.exp.conf.annotations import AnnotationsTypes
from secuml.exp.conf.annotations import NoGroundTruth
from secuml.exp.data import annotations_db_tools
from secuml.exp.tools.db_tables import InstancesAlchemy

from .features import FeaturesFromExp


class Instances(CoreInstances):

    def __init__(self, experiment, streaming=False, stream_batch=None):
        self._set_exp_conf(experiment)
        ids, timestamps, gt_labels, gt_families = self._get_instances_from_db()
        ids = Ids(ids, timestamps=timestamps)
        ground_truth = Annotations(gt_labels, gt_families, ids)
        features = FeaturesFromExp(experiment, ids, streaming=streaming,
                                   stream_batch=stream_batch)
        annotations = self._get_annotations(ids, ground_truth)
        CoreInstances.__init__(self, ids, features, annotations, ground_truth)

    def _set_exp_conf(self, experiment):
        self.experiment = experiment
        self.session = experiment.session
        self.exp_conf = experiment.exp_conf
        self.dataset_conf = experiment.exp_conf.dataset_conf
        self.annotations_conf = experiment.exp_conf.annotations_conf

    def _get_annotations(self, ids, ground_truth):
        annotations_type = self.annotations_conf.annotations_type
        if annotations_type == AnnotationsTypes.ground_truth:
            if not self.dataset_conf.has_ground_truth:
                raise NoGroundTruth(self.dataset_conf.dataset)
            return ground_truth
        elif annotations_type == AnnotationsTypes.ground_truth_if_exists:
            if not self.dataset_conf.has_ground_truth:
                return Annotations(None, None, ids)
            return ground_truth
        elif annotations_type == AnnotationsTypes.partial:
            annotations = Annotations(None, None, ids)
            db_res = annotations_db_tools.get_annotated_instances(
                                          self.session,
                                          self.annotations_conf.annotations_id)
            for instance_id, label, family in db_res:
                annotations.set_label_family(instance_id, label, family)
            return annotations

    def _get_instances_from_db(self):
        dataset_id = self.dataset_conf.dataset_id
        query = self.session.query(InstancesAlchemy)
        query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
        query = query.order_by(InstancesAlchemy.id)
        gt_labels, gt_families = None, None
        if self.dataset_conf.has_ground_truth:
            ids, timestamps, gt_labels, gt_families = zip(
                    *[(r.id, r.timestamp, r.label, r.family)
                      for r in query.all()])
            gt_labels = np.array(gt_labels)
            gt_families = np.array(gt_families)
        else:
            ids, timestamps = zip(*[(r.id, r.timestamp) for r in query.all()])
        ids = np.array(ids)
        timestamps = np.array(timestamps)
        return ids, timestamps, gt_labels, gt_families
