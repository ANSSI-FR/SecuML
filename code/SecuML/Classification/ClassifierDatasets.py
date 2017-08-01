## SecuML
## Copyright (C) 2016-2017  ANSSI
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

from __future__ import division
import numpy as np

from SecuML.Data.Instances import Instances

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

# The labels of the testing dataset are erased.
# The true labels are used for the performance evaluation.
class ClassifierDatasets(object):

    def __init__(self, experiment, classification_conf):
        self.experiment           = experiment
        self.classification_conf  = classification_conf
        self.validation_instances = None

    def getFeaturesNames(self):
        return self.train_instances.getFeaturesNames()

    def setValidationInstances(self, validation_instances):
        self.validation_instances = validation_instances
        if self.validation_instances is not None:
            self.validation_instances.eraseLabels()

    def setDatasets(self, train_instances, test_instances):
        self.train_instances = train_instances
        self.test_instances  = test_instances
        self.test_instances.eraseLabels()
        self.setSampleWeights()

    def generateDatasets(self):
        instances = Instances()
        instances.initFromExperiment(self.experiment)
        instances = instances.getAnnotatedInstances()
        test_conf = self.classification_conf.test_conf
        if test_conf.method == 'random_split':
            self.splitTrainDataset(instances, test_conf.test_size)
        elif test_conf.method == 'test_dataset':
            self.generateTrainTestDatasets(instances, test_conf.test_exp)
        elif test_conf.method == 'unlabeled':
            self.unlabeledLabeledDatasets(instances, test_conf.labels_annotations)
        self.test_instances.eraseLabels()
        self.setSampleWeights()

    def setSampleWeights(self):
        if self.classification_conf.sample_weight:
            self.computeSampleWeights()
        else:
            self.sample_weight = None

    def splitTrainDataset(self, instances, test_size):
        labeled_instances = instances.getLabeledInstances()
        train, test = generateTrainTestIds(labeled_instances.getIds(), test_size)
        self.train_instances = labeled_instances.getInstancesFromIds(train)
        self.test_instances = labeled_instances.getInstancesFromIds(test)

    def generateTrainTestDatasets(self, instances, validation_exp):
        self.train_instances = instances
        self.test_instances = Instances()
        self.test_instances.initFromExperiment(validation_exp)

    def unlabeledLabeledDatasets(self, instances, labels_annotations):
        if labels_annotations == 'labels':
            self.train_instances = instances.getLabeledInstances()
        elif labels_annotations == 'annotations':
            self.train_instances = instances.getAnnotatedInstances()
        self.test_instances = instances.getUnlabeledInstances()
        self.test_instances.labels = self.test_instances.true_labels
        self.test_instances.families = self.test_instances.true_families

    def semiSupervisedSplit(self, instances, test_size):
        labeled_instances = instances.getLabeledInstances()
        labeled_train, labeled_test = generateTrainTestIds(labeled_instances.getIds(), test_size)
        unlabeled_instances = instances.getUnlabeledInstances()
        unlabeled_train, unlabeled_test = generateTrainTestIds(unlabeled_instances.getIds(), test_size)
        self.train_instances = instances.getInstancesFromIds(labeled_train + unlabeled_train)
        self.test_instances  = instances.getInstancesFromIds(labeled_test + unlabeled_test)

    def computeSampleWeights(self):
        self.sample_weight = [1] * self.train_instances.numInstances()
        families = self.train_instances.getFamilies()
        families_prop = self.train_instances.getFamiliesProp()
        for i in range(self.train_instances.numInstances()):
            self.sample_weight[i] = 1 / families_prop[families[i]]
            if self.sample_weight[i] > 100:
                self.sample_weight[i] = 100
