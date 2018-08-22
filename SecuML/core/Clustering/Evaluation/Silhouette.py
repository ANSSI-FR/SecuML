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

import matplotlib.pyplot as plt
import numpy as np
import os.path as path

from sklearn.metrics import silhouette_samples

from SecuML.core.Tools import colors_tools


class Silhouette(object):

    def __init__(self, instances):
        self.instances = instances
        self.distances = None

    def generateEvaluation(self, output_dir, assigned_clusters, quick=False):
        if quick:
            self.silhouette_avg = 0
            return
        if self.distances is not None:
            self.sample_silhouette_values = silhouette_samples(
                self.distances, assigned_clusters,
                metric='precomputed')
        else:
            self.sample_silhouette_values = silhouette_samples(self.instances.features.getValues(),
                                                               assigned_clusters)
        self.silhouette_avg = np.mean(self.sample_silhouette_values)
        self.printSilhouette(output_dir, assigned_clusters)

    # Code from a scikit-learn example:
    # Selecting the number of clusters with silhouette analysis on KMeans clustering
    def printSilhouette(self, output_dir, assigned_clusters):
        num_clusters = len(set(assigned_clusters))
        plt.clf()
        y_lower = 10
        all_colors = colors_tools.colors(num_clusters)
        for i in range(num_clusters):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = \
                self.sample_silhouette_values[assigned_clusters == i]
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
        plt.savefig(path.join(output_dir, 'silhouette.png'))
        plt.clf()

    def toJson(self):
        obj = {}
        obj['silhouette_avg'] = self.silhouette_avg
        return obj
