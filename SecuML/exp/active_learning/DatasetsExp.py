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

from SecuML.core.active_learning.Datasets import Datasets

from SecuML.exp.data import annotations_db_tools
from SecuML.exp.data.ExportInstances import ExportInstances


class DatasetsExp(Datasets):

    # Users can update the annotation of previously annotated instances
    # with the predictions and errors analysis interfaces.
    def checkAnnotationsWithDB(self, exp):
        for instance_id in self.instances.annotations.getAnnotatedIds():
            label = self.instances.annotations.getLabel(instance_id)
            family = self.instances.annotations.getFamily(instance_id)
            annotations_conf = exp.exp_conf.annotations_conf
            annotations_type = annotations_conf.annotations_type
            annotations_id = annotations_conf.annotations_id
            dataset_id = exp.exp_conf.dataset_conf.dataset_id
            annotation = annotations_db_tools.getAnnotation(exp.session,
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
    def checkNewAnnotationsWithDB(self, exp):
        for instance_id in self.instances.annotations.getUnlabeledIds():
            annotations_conf = exp.exp_conf.annotations_conf
            annotations_type = annotations_conf.annotations_type
            annotations_id = annotations_conf.annotations_id
            dataset_id = exp.exp_conf.dataset_conf.dataset_id
            annotation = annotations_db_tools.getAnnotation(exp.session,
                                                            annotations_type,
                                                            annotations_id,
                                                            dataset_id,
                                                            instance_id)
            if annotation is not None:
                DB_label, DB_family = annotation
                self.update(instance_id, DB_label, DB_family)

    def saveAnnotatedInstances(self, output_filename, exp):
        instances = self.instances.getAnnotatedInstances()
        export_instances = ExportInstances(instances, exp,
                                           user_instance_ids=True)
        export_instances.exportAnnotations(output_filename)
