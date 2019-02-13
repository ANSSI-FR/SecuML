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

from secuml.core.data.annotations import Annotations
from secuml.core.data.ids import Ids
from secuml.core.data.instances import Instances as CoreInstances
from secuml.core.data import labels_tools
from secuml.exp.tools.db_tables import InstancesAlchemy
from secuml.exp.conf.annotations import AnnotationsTypes
from secuml.exp.data import annotations_db_tools
from secuml.exp.data import get_dataset_ids

from .features import FeaturesFromExp


def get_dataset_timestamps(session, dataset_id):
    query = session.query(InstancesAlchemy)
    query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
    query = query.order_by(InstancesAlchemy.id)
    return [r.timestamp for r in query.all()]


class Instances(CoreInstances):

    def __init__(self, experiment):
        self._set_exp_conf(experiment)
        ids = self.get_ids()
        features = FeaturesFromExp(experiment, ids)
        annotations = self._get_annotations(ids)
        ground_truth = self._get_ground_truth(ids)
        CoreInstances.__init__(self, ids, features, annotations, ground_truth)

    def _set_exp_conf(self, experiment):
        self.experiment = experiment
        self.session = experiment.session
        self.exp_conf = experiment.exp_conf
        self.dataset_conf = experiment.exp_conf.dataset_conf
        self.annotations_conf = experiment.exp_conf.annotations_conf

    def get_ids(self):
        dataset_id = self.dataset_conf.dataset_id
        ids = get_dataset_ids(self.session, dataset_id)
        timestamps = get_dataset_timestamps(self.session, dataset_id)
        return Ids(ids, timestamps=timestamps)

    def _get_annotations(self, ids):
        annotations_type = self.annotations_conf.annotations_type
        if annotations_type == AnnotationsTypes.none:
            return Annotations(None, None, ids)
        if annotations_type == AnnotationsTypes.ground_truth:
            return self._get_ground_truth(ids)
        if annotations_type == AnnotationsTypes.partial:
            annotations = Annotations(None, None, ids)
            db_res = annotations_db_tools.get_annotated_instances(
                                           self.session,
                                           self.annotations_conf.annotations_id)
            for instance_id, label, family in db_res:
                annotations.set_label_family(
                                          instance_id,
                                          labels_tools.label_str_to_bool(label),
                                          family)
            return annotations

    def _get_ground_truth(self, ids):
        if not self.dataset_conf.has_ground_truth:
            return Annotations(None, None, ids)
        dataset_id = self.dataset_conf.dataset_id
        labels, families = annotations_db_tools.get_ground_truth(self.session,
                                                                 dataset_id)
        return Annotations(labels, families, ids)
