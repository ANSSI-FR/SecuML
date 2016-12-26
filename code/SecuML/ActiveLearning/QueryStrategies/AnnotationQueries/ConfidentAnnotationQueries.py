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

## package for float division (/)
## in order to perform integer division (//)
from __future__ import division
import json
import time

from SecuML.ActiveLearning.CheckPredictedLabels import CheckPredictedLabels
from SecuML.Data import labels_tools
from SecuML.Data.Instances import Instances
from SecuML.Experiment import experiment_db_tools
from SecuML.Experiment.ClusteringExperiment import ClusteringExperiment
from SecuML.Tools import matrix_tools

from AnnotationQueries import AnnotationQueries

class ConfidentAnnotationQueries(AnnotationQueries):

    def __init__(self, iteration, label, num_annotations, proba_min, proba_max):
        AnnotationQueries.__init__(self, iteration)
        self.label = label
        self.proba_min = proba_min
        self.proba_max = proba_max
        self.num_annotations = num_annotations

    def addPredictedLabels(self):
        df = matrix_tools.extractRowsWithThresholds(self.predictions,
                self.proba_min, self.proba_max, 'predicted_proba')
        self.predicted_ids = list(df.index)
    
    def analyzePredictedLabels(self):
        datasets = self.iteration.datasets
        al_experiment = self.iteration.experiment
        self.annotated_instances = datasets.getAnnotatedInstances(label = self.label)
        num_sublabels = len(self.annotated_instances.getSublabelsValues())
        num_clusters = max(2, num_sublabels)
        clustering_analysis = len(self.predicted_ids) >= num_clusters
        experiment_db_tools.addPredictedLabelsAnalysis(
                self.iteration.experiment.cursor,
                self.iteration.experiment.experiment_id,
                self.iteration.iteration_number,
                self.label,
                clustering_analysis)
        al_experiment.db.commit()
        if clustering_analysis:
            clustering_experiment = self.createClusteringExperiment(num_clusters)
            start_time = time.time()
            self.clustering(clustering_experiment)
            self.clustering_time = time.time() - start_time
        else:
            self.clustering_analysis = None
            self.clustering_time = 0

    def generateAnnotationQueries(self):
        if self.clustering_analysis is None:
            self.exportAnnotationQueries(self.predicted_ids, self.label)
            return
        clustering = self.clustering_analysis.clustering
        num_clusters = self.clustering_analysis.num_clusters
        r = self.iteration.experiment.ilab_conf.r
        if r is None:
            weights = self.computeClusterWeights(clustering)
            num_annotations = self.computeNumAnnotationsPerCluster(clustering, weights)
        else:
            num_annotations = [r] * num_clusters
        self.annotation_queries = {}
        for c in range(num_clusters):
            cluster_id = 'c_' + str(c)
            self.annotation_queries[cluster_id] = clustering.getClusterInstances(c, 
                    num_annotations[c], drop_instances = self.annotated_instances.getIds())
            cluster_label = clustering.getClusterLabel(c)
        filename  = self.iteration.output_directory
        filename += 'toannotate_' + self.label + '.csv'
        with open(filename, 'w') as f:
            json.dump(self.annotation_queries, f, indent = 2)

    def annotateAuto(self):
        self.add_labels = CheckPredictedLabels(self.iteration)
        labeled_instances = set(self.annotated_instances.getIds())
        label_method = 'AL_checking_clustering_' + self.label
        if self.clustering_analysis is None:
            self.annotateClusterInstances(label_method)
            return
        ilab_conf = self.iteration.experiment.ilab_conf
        for cluster_id in range(len(self.annotation_queries)):
            self.checkCluster(cluster_id, ilab_conf,
                    label_method, labeled_instances)
        self.iteration.experiment.db.commit()

    def clustering(self, clustering_experiment):
        datasets = self.iteration.datasets
        predicted_instances = datasets.getInstancesFromIds(self.predicted_ids)
        clustering_conf = clustering_experiment.conf
        instances = Instances()
        instances.union(predicted_instances, self.annotated_instances)
        self.clustering_analysis = clustering_conf.algo(instances, 
                clustering_experiment)
        self.clustering_analysis.run(quick = True)

    def createClusteringExperiment(self, num_clusters):
        exp = self.iteration.experiment
        name = '-'.join([exp.experiment_name, 
            str(self.iteration.iteration_number), 
            self.label])
        clustering_conf = exp.ilab_conf.clustering_conf
        clustering_conf.setNumClusters(num_clusters)
        clustering_experiment = ClusteringExperiment(
                exp.project, exp.dataset, exp.db, exp.cursor, 
                clustering_conf,
                experiment_name = name,
                experiment_label = exp.experiment_label,
                parent = exp.experiment_id)
        clustering_experiment.setFeaturesFilenames(exp.features_filenames)
        clustering_experiment.createExperiment()
        clustering_experiment.export()
        return clustering_experiment
    
    def annotateClusterInstances(self, label_method):
        ids = self.predicted_ids
        true_labels = self.add_labels.getTrueLabels(ids)
        true_sublabels = self.add_labels.getTrueSublabels(ids)
        for i in range(len(true_labels)):
            self.add_labels.addLabel(ids[i], true_labels[i],
                    true_sublabels[i], label_method + '__annotation',
                    True)
    
    def checkCluster(self, cluster_id,
            ilab_conf, label_method, labeled_instances):
        annotation_queries = self.annotation_queries['c_' + str(cluster_id)]
        num_annotations = sum([len(annotation_queries[i]) for i in ['c', 'e', 'r']])
        if num_annotations == 0:
            return
        sublabel = None
        num_homogeneous = 0
        homogeneous_center, sublabel, num_homogeneous = self.checkClusterPart(annotation_queries['c'],
                label_method + '__c__annotation',
                ilab_conf, sublabel, labeled_instances, num_homogeneous)
        if homogeneous_center or not ilab_conf.stop_heterogeneous:
            homogeneous_edge, sublabel, num_homogeneous = self.checkClusterPart(annotation_queries['e'],
                    label_method + '__e__annotation',
                    ilab_conf, sublabel, labeled_instances, num_homogeneous)
        if homogeneous_edge or not ilab_conf.stop_heterogeneous:
            homogeneous_random, sublabel, num_homogeneous = self.checkClusterPart(annotation_queries['r'],
                    label_method + '__r_annotation',
                    ilab_conf, sublabel, labeled_instances, num_homogeneous)
        if ilab_conf.semiauto: 
            if homogeneous_center and homogeneous_edge and homogeneous_random:
                self.labelWholeCluster(
                        label_method + '__cluster', cluster_id, 
                        sublabel, labeled_instances)
    
    def checkClusterPart(self, annotation_queries, label_method,
            ilab_conf, part_sublabel, labeled_instances, num_homogeneous):
        if len(annotation_queries) == 0:
            return True, part_sublabel, num_homogeneous
        true_labels = self.add_labels.getTrueLabels(annotation_queries)
        true_sublabels = self.add_labels.getTrueSublabels(annotation_queries)
        if part_sublabel is None:
            part_sublabel = true_sublabels[0]
        homogeneous = True
        for i in range(len(annotation_queries)):
            instance = annotation_queries[i]
            label = true_labels[i]
            sublabel = true_sublabels[i]
            if instance not in labeled_instances:
                self.add_labels.addLabel(instance, label, sublabel, label_method,
                        True)
                labeled_instances.add(instance)
            if self.label != label or part_sublabel != sublabel:
                ## The clustering is not homogeneous
                homogeneous = False
                if ilab_conf.stop_heterogeneous:
                    return homogeneous, part_sublabel, num_homogeneous
            else:
                num_homogeneous += 1
        return homogeneous, part_sublabel, num_homogeneous
    
    def labelWholeCluster(self, label_method,
            cluster_id, sublabel, labeled_instances):
        clustering = self.clustering_analysis.clustering
        instances = clustering.clusters[cluster_id].instances_ids
        for instance in instances:
            if instance not in labeled_instances:
                self.add_labels.addLabel(instance, self.label, sublabel, label_method,
                        False)
                labeled_instances.add(instance)
        
    def computeNumAnnotationsPerCluster(self, clustering, weights):
        num_clusters = clustering.num_clusters
        num_annotations = [-1] * num_clusters
        card = [0] * num_clusters
        remaining_annotations = self.num_annotations
        num_remaining_clusters = num_clusters
        # Assign the number of annotations to clusters where w_k * N < |C_k|
        for c in range(num_clusters):
            card[c] = clustering.clusters[c].num_instances
            if card[c] <= weights[c]*self.num_annotations:
                num_annotations[c] = card[c]
                remaining_annotations -= num_annotations[c]
                num_remaining_clusters -= 1
        # Update the weights and assign the number of annotations to the other clusters
        for c in range(num_clusters):
            if num_annotations[c] != -1:
                continue
            new_weight = weights[c] * num_clusters / num_remaining_clusters
            num_annotations[c] = int(new_weight*remaining_annotations)
            remaining_annotations -= num_annotations[c]
        # Assign the remaining instances to the first clusters
        while remaining_annotations > 0 or sum(num_annotations) == sum(card):
            for c in range(num_clusters):
                if remaining_annotations == 0:
                    break
                if card[c] > num_annotations[c]:
                    num_annotations[c] += 1
                    remaining_annotations -= 1
        return num_annotations

    def computeClusterWeights(self, clustering):
        cluster_weights = self.iteration.experiment.ilab_conf.cluster_weights
        num_clusters = clustering.num_clusters
        if cluster_weights == 'uniform':
            return [1 / num_clusters] * num_clusters
