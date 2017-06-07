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
import json
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

from Evaluation.ClusteringEvaluation import ClusteringEvaluation
from Cluster import Cluster
from SecuML.Tools import dir_tools

class Clustering(object):

    def __init__(self, experiment, instances, assigned_clusters, clustering_algo = None):
        self.experiment        = experiment
        self.instances         = instances
        self.assigned_clusters = assigned_clusters
        self.num_clusters      = len(set(assigned_clusters))
        self.clustering_algo   = clustering_algo
        self.evaluation        = ClusteringEvaluation(self.instances,
                                                      self.assigned_clusters,
                                                      self.clustering_algo)
        self.setOutputDirectory()

    def numClusters(self):
        return self.num_clusters

    def setOutputDirectory(self):
        self.output_directory = dir_tools.getExperimentOutputDirectory(
                self.experiment)

    def generateClustering(self, assignment_proba, centroids, drop_annotated_instances = False):
        self.clusters = [Cluster() for x in range(self.num_clusters)]
        ids = self.instances.getIds()
        for i in range(len(ids)):
            instance_id = ids[i]
            annotated   = self.instances.isAnnotated(instance_id)
            c           = self.assigned_clusters[i]
            proba       = None
            if assignment_proba is not None:
                proba       = assignment_proba[i, :]
            label       = self.instances.getLabel(instance_id)
            family    = self.instances.getFamily(instance_id)
            if centroids is not None:
                # Reshape to avoid warning from euclidean_distances
                # Does not take 1D array as input
                centroid = centroids[c].reshape(1, -1)
                features = np.array(self.instances.getInstance(instance_id)).reshape(1,-1)
                distance = euclidean_distances(centroid, features)[0][0]
            else:
                distance = None
            self.clusters[c].addInstance(instance_id, distance, label, family, annotated)
        unknown_cluster_id = 0
        for c in range(self.num_clusters):
            unknown_cluster_id = self.clusters[c].finalComputation(unknown_cluster_id)
        self.clusteringToJson(drop_annotated_instances = drop_annotated_instances)

    def generateEvaluation(self, quick = False):
        self.evaluation.generateEvaluation(quick = quick)
        obj = self.evaluation.toJson()
        filename = self.output_directory + 'clustering_evaluation.json'
        with open(filename, 'w') as f:
            json.dump(obj, f, indent = 2)

    @staticmethod
    def fromJson(experiment):
        clustering = Clustering(experiment, None, [], None)
        with open(clustering.output_directory + 'clusters.json', 'r') as f:
            obj = json.load(f)
            clustering.assigned_clusters = obj['assigned_clusters']
            clustering.num_clusters = len(obj) - 1
            clustering.clusters = [Cluster() for x in range(clustering.num_clusters)]
            for c in range(clustering.num_clusters):
                clustering.clusters[c] = Cluster.fromJson(obj[str(c)])
        return clustering

    def clusteringToJson(self, drop_annotated_instances = False):
        obj = {}
        obj['assigned_clusters'] = list(map(int, self.assigned_clusters))
        if drop_annotated_instances:
            drop_instances = self.instances.getLabeledIds()
        else:
            drop_instances = None
        for c in range(self.num_clusters):
            obj[str(c)] = self.clusters[c].toJson(drop_instances = drop_instances)
        filename = self.output_directory + 'clusters.json'
        with open(filename, 'w') as f:
            json.dump(obj, f, indent = 2)

    def getClusterLabel(self, selected_cluster):
        return self.clusters[selected_cluster].getClusterLabel()

    # c: center
    # e: edge (does not return instances from the center)
    # r: random (does not return instances from the center and the edge)
    # An instance cannot be in two sets among c, e and r.
    def getClusterInstancesVisu(self, selected_cluster, num_instances, random = False,
            drop_instances = None):
        return self.clusters[selected_cluster].getClusterInstancesVisu(num_instances, random, drop_instances)

    def getClusterLabelsFamilies(self, selected_cluster):
        return self.clusters[selected_cluster].getClusterLabelsFamilies(self.experiment.cursor,
                self.experiment.experiment_label_id)

    def getClusterLabelFamilyIds(self, selected_cluster, label, family):
        return self.clusters[selected_cluster].getClusterLabelFamilyIds(label, family,
                self.experiment.cursor, self.experiment.experiment_label_id)

    ## Remove semi automatic labels
    ## Annotations are preserved
    def removeClusterLabel(self, selected_cluster, num_results):
        self.clusters[selected_cluster].removeClusterLabel(num_results,
                self.experiment.cursor, self.experiment.experiment_label_id)

    def addClusterLabel(self, selected_cluster, num_results,
            label, family, label_iteration, label_method):
        self.clusters[selected_cluster].addClusterLabel(num_results, label, family, self.experiment.cursor,
                self.experiment.experiment_label_id, label_iteration, label_method)
