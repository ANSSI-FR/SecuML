# SecuML
# Copyright (C) 2017  ANSSI
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

from SecuML.core.Data.Instances import Instances
from SecuML.core.Data import labels_tools

from SecuML.experiments import db_tables
from SecuML.experiments.Data import annotations_db_tools


class InstancesFromExperiment(object):

    def __init__(self, experiment):
        self.experiment = experiment

    def getInstances(self):
        ids = self.getIds()
        features, features_names, features_descriptions = self.getFeatures()
        labels, families, gt_labels, gt_families = self.getLabels(len(ids))
        instances = Instances(ids, features,
                              features_names, features_descriptions,
                              labels, families,
                              gt_labels, gt_families)
        return instances

    def getIds(self):
        ids = db_tables.getDatasetIds(self.experiment.session,
                                      self.experiment.dataset_id)
        self.indexes = {}
        for i in range(len(ids)):
            self.indexes[ids[i]] = i
        return ids

    def getFeatures(self):
        features = self.experiment.getAllFeatures()
        names, descriptions = self.experiment.getFeaturesNamesDescriptions()
        return features, names, descriptions

    def getLabels(self, num_instances):
        labels = [None] * num_instances
        families = [None] * num_instances
        gt_labels = [None] * num_instances
        gt_families = [None] * num_instances
        # Labels/Families
        benign_ids = annotations_db_tools.getLabelIds(self.experiment.session,
                                                      self.experiment.experiment_id,
                                                      labels_tools.BENIGN)
        malicious_ids = annotations_db_tools.getLabelIds(self.experiment.session,
                                                         self.experiment.experiment_id,
                                                         labels_tools.MALICIOUS)
        for instance_id in benign_ids + malicious_ids:
            label, family, method = annotations_db_tools.getAnnotationDetails(
                self.experiment.session,
                self.experiment.experiment_id,
                instance_id)
            labels[self.indexes[instance_id]
                   ] = labels_tools.labelStringToBoolean(label)
            families[self.indexes[instance_id]] = family
        # True Labels
        has_ground_truth = db_tables.hasGroundTruth(self.experiment)
        if has_ground_truth:
            gt_labels, gt_families = annotations_db_tools.getGroundTruth(
                self.experiment.session,
                self.experiment.experiment_id)
        return labels, families, gt_labels, gt_families
