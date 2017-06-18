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
import csv
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.preprocessing import StandardScaler

from SecuML.Data import idents_tools
from SecuML.Data import labels_tools
from SecuML.Tools import dir_tools

class Instances(object):

    def __init__(self):
        self.features       = None
        self.features_names = None
        self.ids            = None
        ## labels and true_labels contain booleans
        ## (True -> Malicious, False -> Benign)
        ## None if the instance is unlabeled
        self.labels        = None
        self.families      = None
        self.true_labels   = None
        self.true_families = None
        self.annotations   = None

    def initFromExperiment(self, experiment):
        self.initFromCsvFiles(experiment.getFeaturesFilesFullpaths())
        self.setLabelsFromExperiment(experiment)

    def initFromMatrix(self, ids, matrix, features_names,
                       labels = None, families = None,
                       true_labels = None, true_families = None,
                       annotations = None):
        self.setIds(ids)
        self.features       = matrix
        self.features_names = features_names
        self.labels         = labels
        self.families       = families
        self.true_labels    = true_labels
        self.true_families  = true_families
        self.annotations    = annotations

    def initFromCsvFiles(self, csv_files):
        self.features_names = []
        self.features = None
        for csv_file in csv_files:
            with open(csv_file, 'r') as f:
                features = f.readline().strip('\n').split(',')[1:]
                self.features_names += features
                features = list(list(rec) for rec in csv.reader(f,
                    quoting = csv.QUOTE_NONNUMERIC))
                self.setIds([int(l[0]) for l in features])
                if self.features is None:
                    self.features = [l[1:] for l in features]
                else:
                    self.features = [f1 + f2[1:] for f1, f2 in zip(self.features, features)]

    def union(self, instances_1, instances_2):
        self.initFromMatrix(
                instances_1.ids + instances_2.ids,
                instances_1.features + instances_2.features,
                instances_1.features_names,
                labels = instances_1.labels + instances_2.labels,
                families = instances_1.families + instances_2.families,
                true_labels = instances_1.true_labels + instances_2.true_labels,
                true_families = instances_1.true_families + instances_2.true_families,
                annotations = instances_1.annotations + instances_2.annotations)

    def createDataset(self, project, dataset, features_filenames, cursor):
        dataset_dir, features_dir, init_labels_dir = dir_tools.createDataset(project, dataset)
        self.exportIdents(dataset_dir + 'idents.csv', cursor)
        self.toCsv(features_dir + features_filenames)
        self.saveInstancesLabels(init_labels_dir + 'true_labels.csv')

    def exportIdents(self, output_filename, cursor):
        with open(output_filename, 'w') as f:
            print >>f, 'instance_id,ident'
            ids = self.getIds()
            idents = idents_tools.getAllIdents(cursor)
            for i in range(self.numInstances()):
                print >>f, str(ids[i]) + ','  + idents[i].encode('utf-8')

    def toCsv(self, output_filename):
        header = ['instance_id'] + self.features_names
        with open(output_filename, 'w') as f:
            print >>f, ','.join(header)
            for instance_id in self.getIds():
                print >>f, str(instance_id) + ',' + ','.join(map(str, self.getInstance(instance_id)))

    def saveInstancesLabels(self, output_filename):
        with open(output_filename, 'w') as f:
            print >>f, 'instance_id,label,family'
            for i in range(self.numInstances()):
                instance_id = self.ids[i]
                label = 'malicious' if self.labels[i] else 'benign'
                family = self.families[i]
                print >>f, str(instance_id) + ',' + label + ',' + family

    ##############
    ### Labels ###
    ##############

    def hasTrueLabels(self):
        return all(l is not None for l in self.true_labels)

    def setLabelsFromExperiment(self, experiment):
        num_instances = self.numInstances()
        self.labels = [None] * num_instances
        self.families = [None] * num_instances
        self.annotations = [None] * num_instances
        self.true_labels = [None] * num_instances
        self.true_families = [None] * num_instances
        ## Labels/Families
        benign_ids = labels_tools.getLabelIds(experiment.cursor, 'benign',
                experiment_label_id = experiment.experiment_label_id)
        malicious_ids = labels_tools.getLabelIds(experiment.cursor, 'malicious',
                experiment_label_id = experiment.experiment_label_id)
        for instance_id in benign_ids + malicious_ids:
            label, family, method, annotation = labels_tools.getLabelDetails(
                    experiment.cursor, instance_id,
                    experiment.experiment_label_id)
            self.setLabel(instance_id, label == 'malicious')
            self.setFamily(instance_id, family)
            self.setAnnotation(instance_id, annotation)
        ## True Labels
        if labels_tools.hasTrueLabels(experiment.cursor):
            labels, families = labels_tools.getExperimentLabelsFamilies(experiment.cursor,
                    experiment_label_id = 1)
            self.true_labels    = labels
            self.true_families = families

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

    def checkLabelsWithDB(self, cursor, experiment_label_id):
        for instance_id in self.getAnnotatedIds():
            label  = self.getLabel(instance_id)
            family = self.getFamily(instance_id)
            try:
                DB_label, DB_family, m, annotation = labels_tools.getLabelDetails(
                        cursor,
                        instance_id,
                        experiment_label_id)
                DB_label = labels_tools.labelStringToBoolean(DB_label)
                if DB_label != label or DB_family != family:
                    self.setLabel(instance_id, DB_label)
                    self.setFamily(instance_id, DB_family)
                    self.setAnnotation(instance_id, annotation)
            except labels_tools.NoLabel:
                ## The instance is not annotated anymore
                self.setLabel(instance_id, None)
                self.setFamily(instance_id, None)
                self.setAnnotation(instance_id, None)

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
            l = label == 'malicious'
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
        y = [self.getLabel(i) for i in instance_ids]
        z = [self.getFamily(i) for i in instance_ids]
        num_selected_instances = len(y)
        y_true = [None] * num_selected_instances
        z_true = [None] * num_selected_instances
        if self.hasTrueLabels():
            y_true = [self.getLabel(i, true_labels = True) for i in instance_ids]
            z_true = [self.getFamily(i, true_labels = True) for i in instance_ids]
        selected_instances = Instances()
        annotations = [self.isAnnotated(i) for i in instance_ids]
        selected_instances.initFromMatrix(instance_ids, X, self.getFeaturesNames(),
                labels = y, families = z,
                true_labels = y_true, true_families = z_true,
                annotations = annotations)
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
        return [self.features[i][feature_index] for i in range(self.numInstances())]
