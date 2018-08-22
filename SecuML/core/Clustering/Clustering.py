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

import json
from sklearn.metrics.pairwise import euclidean_distances
import os.path as path

from .Evaluation.ClusteringEvaluation import ClusteringEvaluation
from .Cluster import Cluster


class Clustering(object):

    def __init__(self, instances, assigned_clusters, clustering_algo=None):
        self.instances = instances
        self.assigned_clusters = assigned_clusters
        if len(assigned_clusters) == 0:
            self.num_clusters = 0
        else:
            self.num_clusters = max(assigned_clusters) + 1
        self.clustering_algo = clustering_algo
        self.evaluation = ClusteringEvaluation(self.instances,
                                               self.assigned_clusters,
                                               self.clustering_algo)

    def numClusters(self):
        return self.num_clusters

    def initClustersList(self, num_clusters):
        self.clusters = [Cluster() for x in range(num_clusters)]

    def generateClustering(self, assignment_proba, centroids, drop_annotated_instances=False,
                           cluster_labels=None):
        self.initClustersList(self.num_clusters)
        if cluster_labels is not None:
            for x in range(self.num_clusters):
                self.clusters[x].label = cluster_labels[x]
        ids = self.instances.ids.getIds()
        for i in range(len(ids)):
            instance_id = ids[i]
            annotated = self.instances.annotations.isAnnotated(instance_id)
            c = self.assigned_clusters[i]
            proba = None
            if assignment_proba is not None:
                proba = assignment_proba[i, :]
            label = self.instances.annotations.getLabel(instance_id)
            family = self.instances.annotations.getFamily(instance_id)
            if centroids is not None:
                # Reshape to avoid warning from euclidean_distances
                # Does not take 1D array as input
                centroid = centroids[c].reshape(1, -1)
                features = self.instances.features.getInstanceFeatures(
                    instance_id).reshape(1, -1)
                distance = euclidean_distances(centroid, features)[0][0]
            else:
                distance = None
            self.clusters[c].addInstance(
                instance_id, distance, label, family, annotated)
        unknown_cluster_id = 0
        for c in range(self.num_clusters):
            unknown_cluster_id = self.clusters[c].finalComputation(
                unknown_cluster_id)

    def generateEvaluation(self, output_directory, quick=False):
        self.evaluation.generateEvaluation(output_directory, quick=quick)
        obj = self.evaluation.toJson()
        filename = output_directory + 'clustering_evaluation.json'
        with open(filename, 'w') as f:
            json.dump(obj, f, indent=2)

    def export(self, directory, drop_annotated_instances=False):
        obj = {}
        obj['assigned_clusters'] = list(map(int, self.assigned_clusters))
        if drop_annotated_instances:
            drop_instances = self.instances.getAnnotatedIds()
        else:
            drop_instances = None
        for c in range(self.num_clusters):
            obj[str(c)] = self.clusters[c].toJson(
                drop_instances=drop_instances)
        filename = path.join(directory, 'clusters.json')
        with open(filename, 'w') as f:
            json.dump(obj, f, indent=2)

    def getClusterLabel(self, selected_cluster):
        return self.clusters[selected_cluster].getClusterLabel()

    # c: center
    # e: edge (does not return instances from the center)
    # r: random (does not return instances from the center and the edge)
    # An instance cannot be in two sets among c, e and r.
    def getClusterInstancesVisu(self, selected_cluster, num_instances, random=False,
                                drop_instances=None):
        return self.clusters[selected_cluster].getClusterInstancesVisu(num_instances, random, drop_instances)

    @staticmethod
    def fromJson(directory):
        clustering = Clustering(None, [])
        with open(path.join(directory, 'clusters.json'), 'r') as f:
            obj = json.load(f)
            clustering.assigned_clusters = obj['assigned_clusters']
            clustering.num_clusters = len(obj) - 1
            clustering.clusters = [Cluster()
                                   for x in range(clustering.num_clusters)]
            for c in range(clustering.num_clusters):
                clustering.clusters[c] = Cluster.fromJson(obj[str(c)])
        return clustering
