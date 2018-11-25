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

import numpy as np


def generateTrainTestIds(ids, test_size):
    msk = np.random.rand(len(ids)) < 1 - test_size
    train = []
    test = []
    for i in range(len(msk)):
        instance_id = ids[i]
        if msk[i]:
            train.append(instance_id)
        else:
            test.append(instance_id)
    return train, test


class ClassifierDatasets(object):

    def __init__(self, test_conf, sample_weight):
        self.test_conf = test_conf
        self.sample_weight = sample_weight

    def setDatasets(self, train_instances, test_instances, validation_instances):
        self.train_instances = train_instances
        self.test_instances = test_instances
        self.validation_instances = validation_instances
        self.setSampleWeights()

    def getFeaturesIds(self):
        return self.train_instances.features.getIds()

    def generateDatasets(self, instances, test_instances=None,
                         validation_instances=None):
        method = self.test_conf.method
        if method == 'random_split':
            instances = instances.getAnnotatedInstances()
            self.splitTrainDataset(instances, self.test_conf.test_size)
        elif method == 'temporal_split':
            instances = instances.getAnnotatedInstances()
            self.splitTrainDatasetTemporal(instances, self.test_conf.test_size)
        elif method == 'cutoff_time':
            instances = instances.getAnnotatedInstances()
            self.splitTrainDatasetCutoffTime(instances,
                                             self.test_conf.cutoff_time)
        elif method == 'dataset':
            instances = instances.getAnnotatedInstances()
            self.generateTrainTestDatasets(instances, test_instances)
        elif method in ['cv', 'temporal_cv']:
            assert(False)
        elif method == 'unlabeled':
            self.unlabeledLabeledDatasets(instances)
        else:
            assert(False)
        self.setSampleWeights()
        self.validation_instances = validation_instances

    def setSampleWeights(self):
        self.sample_weight = None
        if self.sample_weight:
            self.computeSampleWeights()

    def splitTrainDataset(self, instances, test_size):
        train, test = generateTrainTestIds(instances.ids.getIds(), test_size)
        self.train_instances = instances.getInstancesFromIds(train)
        self.test_instances = instances.getInstancesFromIds(test)

    def splitTrainDatasetTemporal(self, instances, test_size):
        timestamps = instances.ids.timestamps
        ids = instances.ids.ids
        t_ids = list(zip(timestamps, ids))
        t_ids.sort()
        num_train = int(len(t_ids) * (1 - test_size))
        train = [i for t, i in t_ids[:num_train]]
        test = [i for t, i in t_ids[num_train:]]
        self.train_instances = instances.getInstancesFromIds(train)
        self.test_instances = instances.getInstancesFromIds(test)

    def splitTrainDatasetCutoffTime(self, instances, cutoff_time):
        train = instances.ids.getIdsBefore(cutoff_time)
        test = instances.ids.getIdsAfter(cutoff_time)
        self.train_instances = instances.getInstancesFromIds(train)
        self.test_instances = instances.getInstancesFromIds(test)

    def generateTrainTestDatasets(self, instances, test_instances):
        self.train_instances = instances
        self.test_instances = test_instances

    def unlabeledLabeledDatasets(self, instances):
        self.train_instances = instances.getAnnotatedInstances()
        self.test_instances = instances.getUnlabeledInstances()

    def semiSupervisedSplit(self, instances, test_size):
        labeled_instances = instances.getAnnotatedInstances()
        labeled_train, labeled_test = generateTrainTestIds(
            labeled_instances.ids.getIds(), test_size)
        unlabeled_instances = instances.getUnlabeledInstances()
        unlabeled_train, unlabeled_test = generateTrainTestIds(
            unlabeled_instances.ids.getIds(), test_size)
        self.train_instances = instances.getInstancesFromIds(
            labeled_train + unlabeled_train)
        self.test_instances = instances.getInstancesFromIds(
            labeled_test + unlabeled_test)

    def computeSampleWeights(self):
        self.sample_weight = [1] * self.train_instances.numInstances()
        families = self.train_instances.getFamilies()
        families_prop = self.train_instances.getFamiliesProp()
        for i in range(self.train_instances.numInstances()):
            self.sample_weight[i] = 1 / families_prop[families[i]]
            if self.sample_weight[i] > 100:
                self.sample_weight[i] = 100
