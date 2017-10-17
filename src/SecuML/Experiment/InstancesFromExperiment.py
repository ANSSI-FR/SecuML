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

import csv
import numpy as np

from SecuML import db_tables
from SecuML.Data import labels_tools
from SecuML.Data.Instances import Instances

class InstancesFromExperiment(object):

    def __init__(self, experiment):
        self.experiment = experiment

    def getInstances(self):
        ids = self.getIds()
        features, features_names = self.getFeatures()
        labels, families, annotations, true_labels, true_families = self.getLabels(len(ids))
        instances = Instances(ids, features, features_names,
                              labels, families,
                              true_labels, true_families,
                              annotations)
        return instances

    def getIds(self):
        ids = db_tables.getDatasetIds(self.experiment.session, self.experiment.dataset_id)
        self.indexes = {}
        for i in range(len(ids)):
            self.indexes[ids[i]] = i
        return ids

    def getFeatures(self):
        csv_files = self.experiment.getFeaturesFilesFullpaths()
        features_names = []
        features = None
        for csv_file in csv_files:
            with open(csv_file, 'r') as f:
                header = f.readline().strip('\n').split(',')[1:]
                features_names += header
                current_features = list(list(rec) for rec in csv.reader(f,
                    quoting = csv.QUOTE_NONNUMERIC))
                if features is None:
                    features = [l[1:] for l in current_features]
                else:
                    features = [f1 + f2[1:] for f1, f2 in zip(features, current_features)]
        features = np.array(features)
        return features, features_names

    def getLabels(self, num_instances):
        labels        = [None]  * num_instances
        families      = [None]  * num_instances
        annotations   = [False] * num_instances
        true_labels   = [None]  * num_instances
        true_families = [None]  * num_instances
        ## Labels/Families
        benign_ids = labels_tools.getLabelIds(self.experiment, 'benign')
        malicious_ids = labels_tools.getLabelIds(self.experiment, 'malicious')
        for instance_id in benign_ids + malicious_ids:
            label, family, method, annotation = labels_tools.getLabelDetails(self.experiment,
                                                                             instance_id)
            labels[self.indexes[instance_id]] = label == 'malicious'
            families[self.indexes[instance_id]] = family
            annotations[self.indexes[instance_id]] = annotation
        ## True Labels
        has_true_labels = db_tables.hasTrueLabels(self.experiment)
        if has_true_labels:
            true_labels, true_families = labels_tools.getTrueLabelsFamilies(self.experiment)
        return labels, families, annotations, true_labels, true_families
