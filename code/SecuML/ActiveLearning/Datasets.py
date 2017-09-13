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

from SecuML.Data.Instances import Instances
from SecuML.Tools import dir_tools

class Datasets(object):

    def __init__(self, experiment):
        self.experiment = experiment
        self.instances = Instances()
        self.instances.initFromExperiment(experiment)
        self.setValidationInstances(experiment.conf.validation_conf)
        self.initCounts()

    def setValidationInstances(self, validation_conf):
        self.validation_instances = None
        if validation_conf is not None:
            self.validation_instances = Instances()
            self.validation_instances.initFromExperiment(validation_conf.test_exp)

    def update(self, instance_id, label, family, annotation):
        self.new_labels = True
        self.instances.setLabel(instance_id, label == 'malicious')
        self.instances.setFamily(instance_id, family)
        self.instances.setAnnotation(instance_id, annotation)
        ## Update the annotation count
        if annotation:
            self.num_annotations[label] += 1

    def checkLabelsWithDB(self, experiment):
        self.instances.checkLabelsWithDB(experiment)

    def saveLabeledInstances(self, iteration_number):
        for i in ['annotations', 'labels']:
            filename  = dir_tools.getDatasetDirectory(
                    self.experiment.project,
                    self.experiment.dataset)
            filename += 'labels/' + i + '_'
            filename += self.experiment.labeling_method + '_'
            filename += 'exp' + str(self.experiment.experiment_id) + '_'
            filename += 'it' + str(iteration_number) + '.csv'
            if i == 'annotations':
                instances = self.instances.getAnnotatedInstances()
            elif i == 'labels':
                instances = self.instances.getLabeledInstances()
            instances.saveInstancesLabels(filename)

    def numAnnotations(self, label = 'all'):
        if label == 'all':
            num_annotations  = self.numAnnotations('malicious')
            num_annotations += self.numAnnotations('benign')
            return num_annotations
        else:
            return self.num_annotations[label]

    def numLabels(self, label = 'all'):
        if label == 'all':
            num_labels  = self.numLabels('malicious')
            num_labels += self.numLabels('benign')
            return num_labels
        else:
            if label == 'benign':
                return len(self.instances.getBenignIds())
            elif label == 'malicious':
                return len(self.instances.getMaliciousIds())

    def numInstances(self, label = 'all', true_labels = False):
        return self.instances.numInstances(label = label, true_labels = true_labels)

    def getFeaturesNames(self):
        return self.instances.getFeaturesNames()

    def getTrainInstances(self, conf):
        if conf.semi_supervised:
            return self.instances
        else:
            return self.getAnnotatedInstances()

    def getTestInstances(self):
        return self.getUnlabeledInstances()

    def getAnnotatedInstances(self, label = 'all'):
        return self.instances.getAnnotatedInstances(label = label)

    def getLabeledInstances(self):
        return self.instances.getLabeledInstances()

    def getUnlabeledInstances(self):
        return self.instances.getUnlabeledInstances()

    def getInstancesFromIds(self, instance_ids):
        return self.instances.getInstancesFromIds(instance_ids)

    #############################
    #############################
    ##### Private functions #####
    #############################
    #############################

    ## We initial labels have been checked by an expert
    def initCounts(self):
        self.num_instances = {}
        self.num_init = {}
        self.num_annotations = {}
        for label in ['malicious', 'benign']:
            self.num_instances[label] = None
            if self.instances.hasTrueLabels():
                num  = self.instances.numInstances(
                        label = label, true_labels = True)
                self.num_instances[label] = num
            self.num_init[label] = self.getLabeledInstances().numInstances(label = label)
            self.num_annotations[label] = self.num_init[label]
