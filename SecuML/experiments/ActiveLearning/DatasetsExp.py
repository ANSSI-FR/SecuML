# SecuML
# Copyright (C) 2018  ANSSI
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

from SecuML.core.ActiveLearning.Datasets import Datasets
from SecuML.core.Data import labels_tools

from SecuML.experiments.Data import annotations_db_tools
from SecuML.experiments.Data.ExportInstances import ExportInstances


class DatasetsExp(Datasets):

    def checkAnnotationsWithDB(self, experiment):
        for instance_id in self.instances.annotations.getAnnotatedIds():
            label = self.instances.annotations.getLabel(instance_id)
            family = self.instances.annotations.getFamily(instance_id)
            details = annotations_db_tools.getAnnotationDetails(
                experiment.session,
                experiment.experiment_id,
                instance_id)
            if details is None:
                # The instance is not annotated anymore
                self.instances.annotations.setLabelFamily(
                    instance_id, None, None)
            else:
                DB_label, DB_family, m = details
                DB_label = labels_tools.labelStringToBoolean(DB_label)
                if DB_label != label or DB_family != family:
                    self.instances.annotations.setLabelFamily(
                        instance_id, DB_label, DB_family)

    def saveAnnotatedInstances(self, output_filename, exp):
        instances = self.instances.getAnnotatedInstances()
        export_instances = ExportInstances(instances, exp,
                                           user_instance_ids=True)
        export_instances.exportAnnotations(output_filename)
