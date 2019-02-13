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

from secuml.core.active_learning.datasets import Datasets as CoreDatasets

from secuml.exp.data import annotations_db_tools
from secuml.exp.data.export_instances import ExportInstances


class Datasets(CoreDatasets):

    # Users can update the annotation of previously annotated instances
    # with the predictions and errors analysis interfaces.
    def check_annotations_with_db(self, exp):
        for instance_id in self.instances.annotations.get_annotated_ids():
            label = self.instances.annotations.get_label(instance_id)
            family = self.instances.annotations.get_family(instance_id)
            annotations_conf = exp.exp_conf.annotations_conf
            annotations_type = annotations_conf.annotations_type
            annotations_id = annotations_conf.annotations_id
            dataset_id = exp.exp_conf.dataset_conf.dataset_id
            annotation = annotations_db_tools.get_annotation(exp.session,
                                                             annotations_type,
                                                             annotations_id,
                                                             dataset_id,
                                                             instance_id)
            if annotation is None:
                # The instance is not annotated anymore
                self.update(instance_id, None, None)
            else:
                DB_label, DB_family = annotation
                if DB_label != label or DB_family != family:
                    self.update(instance_id, DB_label, DB_family)

    # Users can annotate instances that have not been selected by the active
    # learning strategy with the test panel (predictions barplot).
    def check_new_annotations_with_db(self, exp):
        for instance_id in self.instances.annotations.get_unlabeled_ids():
            annotations_conf = exp.exp_conf.annotations_conf
            annotations_type = annotations_conf.annotations_type
            annotations_id = annotations_conf.annotations_id
            dataset_id = exp.exp_conf.dataset_conf.dataset_id
            annotation = annotations_db_tools.get_annotation(exp.session,
                                                             annotations_type,
                                                             annotations_id,
                                                             dataset_id,
                                                             instance_id)
            if annotation is not None:
                DB_label, DB_family = annotation
                self.update(instance_id, DB_label, DB_family)

    def save_annotations(self, output_filename, exp):
        instances = self.instances.get_annotated_instances()
        export_instances = ExportInstances(instances, exp,
                                           user_instance_ids=True)
        export_instances.export_annotations(output_filename)
