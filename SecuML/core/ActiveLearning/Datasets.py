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

from SecuML.core.Data import labels_tools


class Datasets(object):

    def __init__(self, conf, instances, validation_instances):
        self.conf = conf
        self.instances = instances
        self.validation_instances = validation_instances
        self.initCounts()

    def update(self, instance_id, label, family):
        self.new_annotations = True
        self.instances.annotations.setLabelFamily(
            instance_id,
            labels_tools.labelStringToBoolean(label),
            family)
        # Update the annotation count
        self.num_annotations[label] += 1

    def numAnnotations(self, label='all'):
        return len(self.instances.annotations.getAnnotatedIds(label=label))

    def getFeaturesNames(self):
        return self.instances.features.getNames()

    def getTrainInstances(self, conf):
        if conf.semi_supervised:
            return self.instances
        else:
            return self.getAnnotatedInstances()

    def getTestInstances(self):
        return self.getUnlabeledInstances()

    def getAnnotatedInstances(self, label='all'):
        return self.instances.getAnnotatedInstances(label=label)

    def getUnlabeledInstances(self):
        return self.instances.getUnlabeledInstances()

    def getInstancesFromIds(self, instance_ids):
        return self.instances.getInstancesFromIds(instance_ids)

    def initCounts(self):
        self.ground_truth = {}
        self.num_init = {}
        self.num_annotations = {}
        for label in [labels_tools.MALICIOUS, labels_tools.BENIGN]:
            self.ground_truth[label] = None
            if self.instances.hasGroundTruth():
                num = self.instances.numInstances(
                    label=label, ground_truth=True)
                self.ground_truth[label] = num
            self.num_init[label] = self.getAnnotatedInstances(
                label=label).numInstances()
            self.num_annotations[label] = self.num_init[label]
