## SecuML
## Copyright (C) 2016  ANSSI
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
import random

from SecuML.Data.Instances import Instances

class SupervisedLearningDatasets(object):

    def __init__(self, experiment):
        self.experiment = experiment
        self.validation_instances = None
    
    def getFeaturesNames(self):
        return self.train_instances.getFeaturesNames()

    def setValidationInstances(self, validation_instances):
        self.validation_instances = validation_instances
        self.validation_instances.eraseLabels()

    def generateDatasets(self):
        instances = Instances()
        instances.initFromExperiment(self.experiment)
        test_conf = self.experiment.supervised_learning_conf.test_conf
        if test_conf.method == 'random_split':
            self.splitTrainDataset(instances, test_conf.test_size)
        elif test_conf.method == 'test_dataset':
            self.generateTrainTestDatasets(instances, test_conf.test_exp)
        elif test_conf.method == 'unlabeled':
            self.unlabeledLabeledDatasets(instances, test_conf.labels_annotations)
        self.malicious_instances = instances.getAnnotatedInstances(label = 'malicious')
        if self.experiment.supervised_learning_conf.sample_weight:
            self.computeSampleWeights()
        else:
            self.sample_weight = None
        # The test dataset labels are erased. The true labels are used to perform the validation.
        self.test_instances.eraseLabels()

    def splitTrainDataset(self, instances, test_size):
        labeled_instances = instances.getLabeledInstances()
        labeled_instances_ids = labeled_instances.getIds()
        msk = np.random.rand(labeled_instances.numInstances()) < 1 - test_size
        train = []
        test = []
        for i in range(len(msk)):
            instance_id = labeled_instances_ids[i]
            if msk[i]:
                train.append(instance_id)
            else:
                test.append(instance_id)
        self.train_instances = labeled_instances.getInstancesFromIds(train)
        self.test_instances = labeled_instances.getInstancesFromIds(test)

    def generateTrainTestDatasets(self, instances, validation_exp):
        self.train_instances = instances.getLabeledInstances()
        self.test_instances = Instances()
        self.test_instances.initFromExperiment(validation_exp)

    def unlabeledLabeledDatasets(self, instances, labels_annotations):
        if labels_annotations == 'labels':
            self.train_instances = instances.getLabeledInstances()
        elif labels_annotations == 'annotations':
            self.train_instances = instances.getAnnotatedInstances()
        self.test_instances = instances.getUnlabeledInstances()
        self.test_instances.labels = self.test_instances.true_labels
        self.test_instances.sublabels = self.test_instances.true_sublabels

    def computeSampleWeights(self):
        self.sample_weight = [1] * self.train_instances.numInstances()
        sublabels = self.train_instances.getSublabels()
        sublabels_prop = self.train_instances.getSublabelsProp()
        for i in range(self.train_instances.numInstances()):
            self.sample_weight[i] = 1 / sublabels_prop[sublabels[i]]
            if self.sample_weight[i] > 100:
                self.sample_weight[i] = 100
