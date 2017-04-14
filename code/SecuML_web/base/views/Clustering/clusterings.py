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

from flask import jsonify
from SecuML_web.base import app, db, cursor

from SecuML.Tools import colors_tools
from SecuML.Tools import mysql_tools
from SecuML.Tools import web_tools

from SecuML.Data import labels_tools
from SecuML.Experiment import ExperimentFactory
from SecuML.Plots.BarPlot import BarPlot
from SecuML.Clustering.Clustering import Clustering

@app.route('/getNumElements/<project>/<dataset>/<experiment_id>/<selected_cluster>/')
def getNumElements(project, dataset, experiment_id, selected_cluster):
    selected_cluster = int(selected_cluster)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    cluster = clustering.clusters[selected_cluster]
    res = {}
    res['num_elements'] = cluster.numInstances()
    return jsonify(res)

## c_e_r :
##    c : center
##    e : edge
##    r : random
@app.route('/getClusterInstancesVisu/<project>/<dataset>/<experiment_id>/<selected_cluster>/<c_e_r>/<num_results>/')
def getClusterInstancesVisu(project, dataset, experiment_id, selected_cluster, c_e_r, num_results):
    num_results = int(num_results)
    selected_cluster = int(selected_cluster)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    selected_cluster_ids = {}
    selected_cluster_ids[selected_cluster] = \
            clustering.getClusterInstancesVisu(
                    selected_cluster, num_results, random = True)[c_e_r]
    return jsonify(selected_cluster_ids)

@app.route('/getClustersLabels/<project>/<dataset>/<experiment_id>/')
def getClustersLabels(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    # Do not consider empty clusters for visualization
    labels = []
    for c in range(clustering.num_clusters):
        if clustering.clusters[c].numInstances() > 0:
            labels.append('c_' + str(c))
    return jsonify({'labels': labels})

@app.route('/getClusterLabel/<project>/<dataset>/<experiment_id>/<selected_cluster>/')
def getClusterPredictedLabel(project, dataset, experiment_id, selected_cluster):
    selected_cluster = int(selected_cluster)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    predicted_label = clustering.getClusterLabel(selected_cluster)
    return predicted_label

@app.route('/getClusterLabelsFamilies/<project>/<dataset>/<experiment_id>/<selected_cluster>/')
def getClusterLabelsFamilies(project, dataset, experiment_id, selected_cluster):
    selected_cluster = int(selected_cluster)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    labels_families = clustering.getClusterLabelsFamilies(selected_cluster)
    return jsonify(labels_families)

@app.route('/getClusterLabelFamilyIds/<project>/<dataset>/<experiment_id>/<selected_cluster>/<label>/<family>/<num_results>/')
def getClusterLabelFamilyIds(project, dataset, experiment_id, selected_cluster, label, family, num_results):
    selected_cluster = int(selected_cluster)
    num_results = int(num_results)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    ids = clustering.getClusterLabelFamilyIds(selected_cluster,
            label, family)
    res = web_tools.listResultWebFormat(ids, num_results)
    return jsonify(res)

## Remove only semi automatic labels (the annotations are preserved)
@app.route('/removeClusterLabel/<project>/<dataset>/<experiment_id>/<selected_cluster>/<num_results>/')
def removeClusterLabel(project, dataset, experiment_id, selected_cluster, num_results):
    selected_cluster = int(selected_cluster)
    num_results = int(num_results)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    clustering.removeClusterLabel(selected_cluster, num_results)
    db.commit()
    return ''

@app.route('/addClusterLabel/<project>/<dataset>/<experiment_id>/<selected_cluster>/<num_results>/<label>/<family>/<label_iteration>/<label_method>/')
def addClusterLabel(project, dataset, experiment_id, selected_cluster, num_results, label, family,
        label_iteration, label_method):
    selected_cluster = int(selected_cluster)
    num_results = int(num_results)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    clustering.addClusterLabel(selected_cluster, num_results,
            label, family, label_iteration, label_method)
    db.commit()
    return ''

@app.route('/getClusterStats/<project>/<dataset>/<experiment_id>/')
def getClusterStats(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    experiment_label_id = experiment.experiment_label_id
    clustering = Clustering.fromJson(experiment)
    num_clusters = clustering.num_clusters
    num_unknown_v   = []
    num_malicious_v = []
    num_benign_v    = []
    labels          = []
    mysql_tools.useDatabase(cursor, project, dataset)
    for c in range(num_clusters):
        instances_in_cluster = clustering.clusters[c].instances_ids
        # the empty clusters are not displayed
        if len(instances_in_cluster) > 0:
            cluster_stats = labels_tools.getUnknownMaliciousBenignStats(
                    cursor, experiment_label_id, instances_in_cluster)
            num_unknown_v.append(cluster_stats['unknown'])
            num_malicious_v.append(cluster_stats['malicious'])
            num_benign_v.append(cluster_stats['benign'])
            labels.append('c_' + str(c))
    barplot = BarPlot(labels)
    barplot.addDataset(num_unknown_v, 'black', 'unknown')
    barplot.addDataset(num_malicious_v, '#d9534f', 'malicious')
    barplot.addDataset(num_benign_v, '#5cb85c', 'benign')
    return jsonify(barplot.barplot)

@app.route('/getClustersColors/<num_clusters>/')
def getClustersColors(num_clusters):
    return jsonify({'colors': colors_tools.colors(num_clusters)})
