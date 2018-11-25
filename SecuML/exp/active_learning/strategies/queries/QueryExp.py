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


from SecuML.core.active_learning.strategies.queries.Query import Query
from SecuML.core.data import labels_tools

from SecuML.exp.data import annotations_db_tools


class QueryExp(Query):

    def annotateAuto(self, iteration, kind):
        instances = iteration.datasets.instances
        label = instances.ground_truth.getLabel(self.instance_id)
        label = labels_tools.labelBooleanToString(label)
        family = instances.ground_truth.getFamily(self.instance_id)
        # Update the datasets
        self.updateDatasets(iteration, label, family)
        # Update in the database
        if kind is not None:
            method = '%s__annotation' % kind
        else:
            method = 'annotation'
        annotations_conf = iteration.experiment.exp_conf.annotations_conf
        annotations_db_tools.addAnnotation(iteration.experiment.session,
                                           annotations_conf.annotations_id,
                                           self.instance_id, label, family,
                                           iteration.iteration_number, method)

    def getManualAnnotation(self, iteration):
        exp = iteration.experiment
        annotations_conf = exp.exp_conf.annotations_conf
        annotations_type = annotations_conf.annotations_type
        annotations_id = annotations_conf.annotations_id
        dataset_id = exp.exp_conf.dataset_conf.dataset_id
        annotation = annotations_db_tools.getAnnotation(exp.session,
                                                        annotations_type,
                                                        annotations_id,
                                                        dataset_id,
                                                        self.instance_id)
        if annotation is None:
            iteration.conf.logger.info('Instance %s has not been annotated.'
                                       % (str(self.instance_id)))
        else:
            label, family = annotation
            self.updateDatasets(iteration, label, family)
