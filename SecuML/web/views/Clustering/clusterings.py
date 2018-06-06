# SecuML
# Copyright (C) 2016-2017  ANSSI
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

from flask import jsonify
import random

from SecuML.web import app
from SecuML.web.views.experiments import updateCurrentExperiment

from SecuML.core.Tools import colors_tools
from SecuML.core.Tools.Plots.BarPlot import BarPlot
from SecuML.core.Tools.Plots.PlotDataset import PlotDataset

from SecuML.experiments.Clustering.ClusteringExp import ClusteringExp


def randomSelection(ids, num_res=None):
    if num_res is None or len(ids) <= num_res:
        return ids
    else:
        return random.sample(ids, num_res)


def listResultWebFormat(ids, num_res=None):
    res = {}
    res['num_ids'] = len(ids)
    res['ids'] = randomSelection(ids, num_res)
    return res


@app.route('/getNumElements/<experiment_id>/<selected_cluster>/')
def getNumElements(experiment_id, selected_cluster):
    selected_cluster = int(selected_cluster)
    experiment = updateCurrentExperiment(experiment_id)
    clustering = ClusteringExp.fromJson(experiment.getOutputDirectory())
    cluster = clustering.clusters[selected_cluster]
    res = {}
    res['num_elements'] = cluster.numInstances()
    return jsonify(res)

# c_e_r :
# c : center
# e : edge
# r : random


@app.route('/getClusterInstancesVisu/<experiment_id>/<selected_cluster>/<c_e_r>/<num_results>/')
def getClusterInstancesVisu(experiment_id, selected_cluster, c_e_r, num_results):
    num_results = int(num_results)
    selected_cluster = int(selected_cluster)
    experiment = updateCurrentExperiment(experiment_id)
    clustering = ClusteringExp.fromJson(experiment.getOutputDirectory())
    selected_cluster_ids = {}
    selected_cluster_ids[selected_cluster] = \
        clustering.getClusterInstancesVisu(
        selected_cluster, num_results, random=True)[c_e_r]
    return jsonify(selected_cluster_ids)


@app.route('/getClustersLabels/<experiment_id>/')
def getClustersLabels(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    clustering = ClusteringExp.fromJson(experiment.getOutputDirectory())
    # Do not consider empty clusters for visualization
    clusters = []
    for c in range(clustering.num_clusters):
        # if clustering.clusters[c].numInstances() > 0:
        clusters.append({'id': c, 'label': clustering.clusters[c].label})
    return jsonify({'clusters': clusters})


@app.route('/getClusterLabel/<experiment_id>/<selected_cluster>/')
def getClusterPredictedLabel(experiment_id, selected_cluster):
    selected_cluster = int(selected_cluster)
    experiment = updateCurrentExperiment(experiment_id)
    clustering = ClusteringExp.fromJson(experiment.getOutputDirectory())
    predicted_label = clustering.getClusterLabel(selected_cluster)
    return predicted_label


@app.route('/getClusterLabelsFamilies/<experiment_id>/<selected_cluster>/')
def getClusterLabelsFamilies(experiment_id, selected_cluster):
    selected_cluster = int(selected_cluster)
    experiment = updateCurrentExperiment(experiment_id)
    clustering = ClusteringExp.fromJson(experiment.getOutputDirectory())
    labels_families = clustering.getClusterLabelsFamilies(
        experiment, selected_cluster)
    return jsonify(labels_families)


@app.route('/getClusterLabelFamilyIds/<experiment_id>/<selected_cluster>/<label>/<family>/<num_results>/')
def getClusterLabelFamilyIds(experiment_id, selected_cluster, label, family, num_results):
    selected_cluster = int(selected_cluster)
    num_results = int(num_results)
    experiment = updateCurrentExperiment(experiment_id)
    clustering = ClusteringExp.fromJson(experiment.getOutputDirectory())
    ids = clustering.getClusterLabelFamilyIds(
        experiment, selected_cluster, label, family)
    res = listResultWebFormat(ids, num_results)
    return jsonify(res)


@app.route('/getClusterStats/<experiment_id>/')
def getClusterStats(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    clustering = ClusteringExp.fromJson(experiment.getOutputDirectory())
    num_clusters = clustering.num_clusters
    num_instances_v = []
    labels = []
    for c in range(num_clusters):
        instances_in_cluster = clustering.clusters[c].instances_ids
        num_instances = len(instances_in_cluster)
        # the empty clusters are not displayed

        # if num_instances > 0:
        num_instances_v.append(num_instances)
        #labels.append('c_' + str(c))
        labels.append(clustering.clusters[c].label)
    barplot = BarPlot(labels)
    dataset = PlotDataset(num_instances_v, 'Num. Instances')
    barplot.addDataset(dataset)
    return jsonify(barplot.toJson())


@app.route('/getClustersColors/<num_clusters>/')
def getClustersColors(num_clusters):
    return jsonify({'colors': colors_tools.colors(num_clusters)})
