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

from SecuML.core.data import labels_tools
from SecuML.core.classification.ClassifierDatasets import ClassifierDatasets


class Datasets(object):

    def __init__(self, instances, validation_instances):
        self.instances = instances
        self.validation_instances = validation_instances
        self.initCounts()

    def update(self, instance_id, label, family):
        self.new_annotations = True
        self.instances.annotations.setLabelFamily(instance_id,
                                       labels_tools.labelStringToBoolean(label),
                                       family)
        # Update the annotation count
        self.num_annotations[label] += 1

    def numAnnotations(self, label='all'):
        return len(self.instances.annotations.getAnnotatedIds(label=label))

    def _get_train_test_instances(self, classifier_conf):
        if classifier_conf.semi_supervised:
            train = self.instances
        else:
            train = self.instances.getAnnotatedInstances()
        test = self.getUnlabeledInstances()
        return train, test

    def getUnlabeledInstances(self):
        return self.instances.getUnlabeledInstances()

    def get_classifier_datasets(self, classifier_conf):
        classifier_datasets = ClassifierDatasets(None,
                                                 classifier_conf.sample_weight)
        train, test = self._get_train_test_instances(classifier_conf)
        classifier_datasets.setDatasets(train, test, self.validation_instances)
        return classifier_datasets

    def initCounts(self):
        self.ground_truth = {}
        self.num_init = {}
        self.num_annotations = {}
        for label in [labels_tools.MALICIOUS, labels_tools.BENIGN]:
            self.ground_truth[label] = None
            if self.instances.hasGroundTruth():
                num = self.instances.numInstances(label=label,
                                                  ground_truth=True)
                self.ground_truth[label] = num
            self.num_init[label] = self.instances.getAnnotatedInstances(
                    label=label).numInstances()
            self.num_annotations[label] = self.num_init[label]
