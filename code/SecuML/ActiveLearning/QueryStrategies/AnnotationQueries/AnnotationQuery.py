## SecuML
## Copyright (C) 2017  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

from SecuML.Data import labels_tools

class NoAnnotationBudget(Exception):
    def __str__(self):
        return 'The annotation budget has run out'

class AnnotationQuery(object):

    def __init__(self, instance_id, predicted_proba, suggested_label, suggested_family):
        self.instance_id        = instance_id
        self.predicted_proba    = predicted_proba
        self.suggested_label    = suggested_label
        self.suggested_family = suggested_family

    def displayHeader(self, f):
        print >>f, 'instance_id,predicted_proba,suggested_label,suggested_family'

    def export(self, f):
        line = [self.instance_id, self.predicted_proba, self.suggested_label,
                self.suggested_family]
        line = ','.join(map(str, line))
        print >>f, line

    def toJson(self):
        obj = {}
        obj['instance_id']        = self.instance_id
        obj['predicted_proba']    = self.predicted_proba
        obj['suggested_label']    = self.suggested_label
        obj['suggested_family'] = self.suggested_family
        return  obj

    def annotateAuto(self, iteration, kind):
        instances = iteration.datasets.instances
        label     = instances.getLabel(self.instance_id, true_labels = True)
        label     = labels_tools.labelBooleanToString(label)
        family  = instances.getFamily(self.instance_id, true_labels = True)
        method    = kind + '__annotation'
        if iteration.budget <= 0:
            raise NoAnnotationBudget()
        iteration.budget -= 1
        labels_tools.addLabel(iteration.experiment.cursor,
                              iteration.experiment.experiment_label_id,
                              self.instance_id, label, family,
                              iteration.iteration_number, method, True)
        iteration.datasets.update(self.instance_id, label, family, True)
        iteration.experiment.db.commit()
        return label, family
