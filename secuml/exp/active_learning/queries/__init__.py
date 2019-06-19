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

from secuml.core.active_learning.queries import Query as CoreQuery
from secuml.exp.data import annotations_db_tools


class Query(CoreQuery):

    def annotate_auto(self, iteration, kind):
        instances = iteration.datasets.instances
        label, family = instances.ground_truth.get_label_family(
                                                            self.instance_id)
        # Update the datasets
        self.update_datasets(iteration, label, family)
        # Update in the database
        if kind is not None:
            method = '%s__annotation' % kind
        else:
            method = 'annotation'
        annotations_conf = iteration.exp.exp_conf.annotations_conf
        annotations_db_tools.add_annotation(iteration.exp.session,
                                            annotations_conf.annotations_id,
                                            self.instance_id, label, family,
                                            iteration.iter_num, method)

    def get_manual_annotation(self, iteration):
        annotations_conf = iteration.exp.exp_conf.annotations_conf
        annotations_type = annotations_conf.annotations_type
        annotations_id = annotations_conf.annotations_id
        dataset_id = iteration.exp.exp_conf.dataset_conf.dataset_id
        annotation = annotations_db_tools.get_annotation(iteration.exp.session,
                                                         annotations_type,
                                                         annotations_id,
                                                         dataset_id,
                                                         self.instance_id)
        if annotation is None:
            iteration.conf.logger.info('Instance %s has not been annotated.'
                                       % (str(self.instance_id)))
        else:
            label, family = annotation
            self.update_datasets(iteration, label, family)
