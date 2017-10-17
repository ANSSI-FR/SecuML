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
from scipy.sparse import csr_matrix

from SecuML.Data import labels_tools

class InvalidInstances(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class Instances(object):

    def __init__(self, ids, features, features_names, labels, families,
                 true_labels, true_families, annotations):
        self.setIds(ids)
        self.features       = np.array(features)
        self.features_names = features_names
        self.labels         = labels
        self.families       = families
        self.true_labels    = true_labels
        self.true_families  = true_families
        self.annotations    = annotations
        self.idents        = None         ## TODO
        self.checkValidity()

    def setIdents(self, idents):
        self.idents = idents

    def checkValidity(self):
        message = None
        num_instances = len(self.ids)

        if num_instances != 0:
            if self.features.shape[0] != num_instances:
                message  = 'There are ' + str(num_instances) + ' instances '
                message += 'but the features of ' + str(self.features.shape[0]) + ' instances are provided.'
            elif len(self.features_names) != self.features.shape[1]:
                message  = 'There are ' + str(self.features.shape[1]) + ' features '
                message += 'but ' + str(len(self.features_names)) + ' features names are provided.'
        else:
            if self.features.size != 0:
                message  = 'There is 0 instance but some features are provided.'

        if len(self.labels) != num_instances:
            message  = 'There are ' + str(num_instances) + ' instances '
            message += 'but ' + str(len(self.labels)) + ' labels are provided.'
        elif  len(self.true_labels) != num_instances:
            message  = 'There are ' + str(num_instances) + ' instances '
            message += 'but ' + str(len(self.true_labels)) + ' true labels are provided.'
        elif len(self.families) != num_instances:
            message  = 'There are ' + str(num_instances) + ' instances '
            message += 'but ' + str(len(self.families)) + ' families are provided.'
        elif len(self.true_families) != num_instances:
            message  = 'There are ' + str(num_instances) + ' instances '
            message += 'but ' + str(len(self.true_families)) + ' true families are provided.'
        elif len(self.annotations) != num_instances:
            message  = 'There are ' + str(num_instances) + ' instances '
            message += 'but ' + str(len(self.annotations)) + ' annotations are provided.'

        if message is not None:
            raise InvalidInstances(message)

    # The union must be used on instances coming from the same dataset.
    # Otherwise, there may be some collisions on the ids.
    def union(self, instances):
        if instances.numInstances() == 0:
            return
        # TODO: check consitent dimensions
        if self.numInstances() == 0:
            self.features = instances.features
        else:
            self.features = np.vstack((self.features, instances.features))
        self.setIds(self.ids + instances.ids)
        self.labels         = self.labels + instances.labels
        self.families       = self.families + instances.families
        self.true_labels    = self.true_labels + instances.true_labels
        self.true_families  = self.true_families + instances.true_families
        self.annotations    = self.annotations + instances.annotations
        self.idents         = None # TODO
        self.checkValidity()

    ##############
    ### Labels ###
    ##############

    def hasTrueLabels(self):
        return all(l is not None for l in self.true_labels)

    def getLabels(self, true_labels = False):
        if true_labels:
            return self.true_labels
        else:
            return self.labels

    def getLabel(self, instance_id, true_labels = False):
        index = self.getIndex(instance_id)
        if true_labels:
            return self.true_labels[index]
        else:
            return self.labels[index]

    def setLabel(self, instance_id, label, true_labels = False):
        index = self.getIndex(instance_id)
        if true_labels:
            self.true_labels[index] = label
        else:
            self.labels[index] = label

    def setAnnotation(self, instance_id, annotation):
        index = self.getIndex(instance_id)
        self.annotations[index] = annotation

    def isAnnotated(self, instance_id):
        index = self.getIndex(instance_id)
        return self.annotations[index]

    def checkLabelsWithDB(self, experiment):
        for instance_id in self.getAnnotatedIds():
            label  = self.getLabel(instance_id)
            family = self.getFamily(instance_id)
            details = labels_tools.getLabelDetails(experiment, instance_id)
            if details is None:
                ## The instance is not annotated anymore
                self.setLabel(instance_id, None)
                self.setFamily(instance_id, None)
                self.setAnnotation(instance_id, None)
            else:
                DB_label, DB_family, m, annotation = details
                DB_label = labels_tools.labelStringToBoolean(DB_label)
                if DB_label != label or DB_family != family:
                    self.setLabel(instance_id, DB_label)
                    self.setFamily(instance_id, DB_family)
                    self.setAnnotation(instance_id, annotation)

    def numLabelingErrors(self, label = 'all'):
        if not self.hasTrueLabels():
            return 0
        if label == 'malicious':
            ids = self.getMaliciousIds()
        elif label == 'benign':
            ids = self.getBenignIds()
        else:
            ids = self.getLabeledIds()
        errors = [i for i in ids if self.getLabel(i, true_labels = True) != self.getLabel(i)]
        return len(errors)

    def numInstances(self, label = 'all', true_labels = False):
        if label == 'all':
            return len(self.ids)
        if label == 'malicious':
            return len(self.getMaliciousIds(true_labels = true_labels))
        elif label == 'benign':
            return len(self.getBenignIds(true_labels = true_labels))

    def eraseLabels(self):
        self.labels   = [None] * self.numInstances()
        self.families = [None] * self.numInstances()

    #################
    ### Families ###
    #################

    def getFamilies(self, true_labels = False):
        if true_labels:
            return self.true_families
        else:
            return self.families

    def getFamily(self, instance_id, true_labels = False):
        index = self.getIndex(instance_id)
        if true_labels:
            return self.true_families[index]
        else:
            return self.families[index]

    def setFamily(self, instance_id, family):
        index = self.getIndex(instance_id)
        self.families[index] = family

    def getFamilyIds(self, family, true_labels = False):
        return [i for i in self.getIds() if self.getFamily(i, true_labels = true_labels) == family]

    def getFamiliesValues(self, label = 'all', true_labels = False):
        if label == 'all':
            ids = self.getIds()
        else:
            l = label == 'malicious'
            ids = [i for i in self.getIds() if \
                    self.getLabel(i, true_labels = true_labels) is not None \
                    and self.getLabel(i, true_labels = true_labels) == l]
        families = set([self.getFamily(i, true_labels = true_labels) for i in ids])
        return families

    def getFamiliesCount(self, label = 'all', true_labels = False):
        families_values = self.getFamiliesValues(label = label, true_labels = true_labels)
        families_count = {}
        for family in families_values:
            families_count[family]  = len(self.getFamilyIds(family, true_labels = true_labels))
        return families_count

    def getFamiliesProp(self, label = 'all', true_labels = False):
        families_prop = self.getFamiliesCount(label = label, true_labels = true_labels)
        for family in families_prop.keys():
            families_prop[family] /= self.numInstances(label = label, true_labels = true_labels)
        return families_prop

    def getConnectivityMatrix(self, sparse = True):
        families_ids = {}
        for index in range(self.numInstances()):
            family = self.families[index]
            if family is not None:
                if family not in families_ids:
                    families_ids[family] = []
                families_ids[family].append(index)
        connectivity = np.zeros((self.numInstances(), self.numInstances()),
                dtype = np.int32)
        for family in families_ids.keys():
            for i in families_ids[family]:
                for j in families_ids[family]:
                    connectivity[i, j] = 1
                for family_ in families_ids.keys():
                    if family == family_:
                        continue
                    for j in families_ids[family_]:
                        connectivity[i, j] = -1
        if sparse:
            return csr_matrix(connectivity)
        else:
            return connectivity

    ###########
    ### Ids ###
    ###########

    def setIds(self, ids):
        self.ids = ids
        self.indexes = {}
        for i in range(len(self.ids)):
            self.indexes[self.ids[i]] = i

    def getIndex(self, instance_id):
        return self.indexes[instance_id]

    def getIds(self):
        return self.ids

    def getLabeledIds(self):
        return [i for i in self.getIds() if self.getLabel(i) is not None]

    def getAnnotatedIds(self, label = 'all'):
        if label == 'all':
            ids = [i for i in self.getIds() if self.getLabel(i) is not None and self.isAnnotated(i)]
        else:
            l = labels_tools.labelStringToBoolean(label)
            ids = [i for i in self.getIds() if self.getLabel(i) == l and self.isAnnotated(i)]
        return ids

    def getUnlabeledIds(self):
        return [i for i in self.getIds() if self.getLabel(i) is None]

    def getMaliciousIds(self, true_labels = False):
        return [i for i in self.getIds() if self.getLabel(i, true_labels = true_labels)]

    def getBenignIds(self, true_labels = False):
        return [i for i in self.getIds() if not self.getLabel(i, true_labels = true_labels)]

    def getUnlabeledInstances(self):
        instance_ids = self.getUnlabeledIds()
        return self.getInstancesFromIds(instance_ids)

    def getLabeledInstances(self):
        instance_ids = self.getLabeledIds()
        return self.getInstancesFromIds(instance_ids)

    def getAnnotatedInstances(self, label = 'all'):
        instance_ids = self.getAnnotatedIds(label = label)
        return self.getInstancesFromIds(instance_ids)

    def getInstancesFromIds(self, instance_ids):
        X = [self.getInstance(i) for i in instance_ids]
        y = [self.getLabel(i)    for i in instance_ids]
        z = [self.getFamily(i)   for i in instance_ids]
        num_selected_instances = len(y)
        y_true = [None] * num_selected_instances
        z_true = [None] * num_selected_instances
        if self.hasTrueLabels():
            y_true = [self.getLabel(i, true_labels = True) for i in instance_ids]
            z_true = [self.getFamily(i, true_labels = True) for i in instance_ids]
        annotations = [self.isAnnotated(i) for i in instance_ids]
        selected_instances = Instances(instance_ids, X, self.getFeaturesNames(),
                                       y, z, y_true, z_true, annotations)
        return selected_instances

    ################
    ### Features ###
    ################

    def getFeaturesNames(self):
        return self.features_names

    def getFeatures(self):
        return self.features

    def numFeatures(self):
        return len(self.features_names)

    def getFeatureIndex(self, feature_name):
        return self.features_names.index(feature_name)

    def getInstance(self, instance_id):
        index = self.getIndex(instance_id)
        return self.features[index]

    def getInstanceFeature(self, instance_id, feature_name):
        feature_index = self.getFeatureIndex(feature_name)
        return self.features[instance_id][feature_index]

    def setInstance(self, instance_id, features):
        index = self.getIndex(instance_id)
        self.features[index] = features

    def getFeatureValues(self, feature_name):
        feature_index = self.getFeatureIndex(feature_name)
        return self.getFeatureValuesFromIndex(feature_index)

    def getFeatureValuesFromIndex(self, feature_index):
        return [self.features[i][feature_index] for i in range(self.numInstances())]
