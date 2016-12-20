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

import matplotlib.pyplot as plt
import numpy as np

from sklearn import metrics
from sklearn.metrics import silhouette_samples

from SecuML.Tools import colors_tools

class ClusteringEvaluation(object):

    def __init__(self, instances, clustering_algo):
        self.instances = instances
        self.clustering_algo = clustering_algo
        self.distances = None

    def generateEvaluation(self, quick = False):
        self.setDistortion()
        self.computeSilhouette(quick = quick)
        if self.instances.true_labels is not None:
            true_labels = self.instances.getLabels(true_labels = True)
            true_sublabels = self.instances.getSublabels(true_labels = True)
            labels_sublabels = [str(x[0]) + '_' + str(x[1]) for x in zip(true_labels, true_sublabels)]
        else:
            labels_sublabels = None
        self.computeHomogeneityCompleteness(labels_sublabels)
        self.computeAdjustedEvaluations(labels_sublabels)

    def setDistortion(self):
        self.distortion =  self.clustering_algo.getDistortion()

    ## The homogeneity and the completeness is computed only if the true labels are available.
    ##  It is computed with the labels are the sublabels.
    def computeHomogeneityCompleteness(self, labels_sublabels):
        if labels_sublabels is None:
            self.homogeneity, self.completeness, self.v_measure = 0, 0, 0
            return
        self.homogeneity, self.completeness, self.v_measure = \
                metrics.homogeneity_completeness_v_measure(labels_sublabels, self.clustering_algo.getLabels())

    def computeAdjustedEvaluations(self, labels_sublabels):
        if labels_sublabels is None:
            self.adjusted_rand_score = 0
            self.adjusted_mutual_info_score = 0
            return
        self.adjusted_rand_score = metrics.adjusted_rand_score(labels_sublabels, self.clustering_algo.getLabels())
        self.adjusted_mutual_info_score = metrics.adjusted_mutual_info_score(labels_sublabels, 
                self.clustering_algo.getLabels())

    def computeSilhouette(self, quick):
        if quick:
            self.silhouette_avg = 0
            return
        if self.distances is not None:
            self.sample_silhouette_values = silhouette_samples(
                    self.distances, self.clustering_algo.getLabels(),
                    metric = 'precomputed')
        else:
            self.sample_silhouette_values = silhouette_samples(self.instances.getFeatures(), 
                    self.clustering_algo.getLabels())
        self.silhouette_avg = np.mean(self.sample_silhouette_values)
        self.printSilhouette()

    # Code from a scikit-learn example: 
    # Selecting the number of clusters with silhouette analysis on KMeans clustering
    def printSilhouette(self):
        num_clusters = self.clustering_algo.num_clusters
        plt.clf()
        y_lower = 10
        all_colors = colors_tools.colors(num_clusters)
        for i in range(num_clusters):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = \
                sample_silhouette_values[self.clustering_algo.getLabels() == i]
            ith_cluster_silhouette_values.sort()
            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i
            color = all_colors[i]
            plt.fill_betweenx(np.arange(y_lower, y_upper),
                              0, ith_cluster_silhouette_values,
                              facecolor=color, edgecolor=color, alpha=0.7)
            # Label the silhouette plots with their cluster numbers at the middle
            plt.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples
        plt.title('The silhouette plot for the various clusters.')
        plt.xlabel('The silhouette coefficient values')
        plt.ylabel('Cluster label')
        # The vertical line for average silhoutte score of all the values
        plt.axvline(x=self.silhouette_avg, color='red', linestyle='--')
        plt.yticks([])  # Clear the yaxis labels / ticks
        plt.xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
        plt.savefig(self.outputFilename('silhouette', '.png'))
        plt.clf()

    def toJson(self):
        obj = {}
        obj['distortion']                 = self.distortion
        obj['homogeneity']                = self.homogeneity
        obj['completeness']               = self.completeness
        obj['v_measure']                  = self.v_measure
        obj['adjusted_rand_score']        = self.adjusted_rand_score
        obj['adjusted_mutual_info_score'] = self.adjusted_mutual_info_score
        obj['silhouette_avg']             = self.silhouette_avg
        return obj
