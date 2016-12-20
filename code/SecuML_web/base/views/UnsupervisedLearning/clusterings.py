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
from SecuML.UnsupervisedLearning.Clustering.Clustering import Clustering

@app.route('/getNumElementsDistortion/<project>/<dataset>/<experiment_id>/<selected_cluster>/')
def getNumElementsDistortion(project, dataset, experiment_id, selected_cluster):
    selected_cluster = int(selected_cluster)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    cluster = clustering.clusters[selected_cluster] 
    res = {}
    res['num_elements'] = cluster.num_instances
    res['distortion'] = cluster.distortion
    return jsonify(res)

## c_e_r :
##    c : center
##    e : edge
##    r : random
@app.route('/getClusterInstances/<project>/<dataset>/<experiment_id>/<selected_cluster>/<c_e_r>/<num_results>/')
def getClusterInstances(project, dataset, experiment_id, selected_cluster, c_e_r, num_results):
    num_results = int(num_results)
    selected_cluster = int(selected_cluster)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    selected_cluster_ids = {}
    selected_cluster_ids[selected_cluster] = \
            clustering.getClusterInstances(
                    selected_cluster, num_results, random = True)[c_e_r]
    return jsonify(selected_cluster_ids)

@app.route('/getClustersLabels/<project>/<dataset>/<experiment_id>/')
def getClustersLabels(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    labels = [clustering.getClusterLabel(c) for c in range(clustering.num_clusters)]
    return jsonify({'labels': labels})

@app.route('/getClusterLabel/<project>/<dataset>/<experiment_id>/<selected_cluster>/')
def getClusterPredictedLabel(project, dataset, experiment_id, selected_cluster):
    selected_cluster = int(selected_cluster)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    predicted_label = clustering.getClusterLabel(selected_cluster)
    return predicted_label

@app.route('/getClusterLabelsSublabels/<project>/<dataset>/<experiment_id>/<selected_cluster>/')
def getClusterLabelsSublabels(project, dataset, experiment_id, selected_cluster):
    selected_cluster = int(selected_cluster)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    labels_sublabels = clustering.getClusterLabelsSublabels(selected_cluster)
    return jsonify(labels_sublabels)

@app.route('/getClusterLabelSublabelIds/<project>/<dataset>/<experiment_id>/<selected_cluster>/<label>/<sublabel>/<num_results>/')
def getClusterLabelSublabelIds(project, dataset, experiment_id, selected_cluster, label, sublabel, num_results):
    selected_cluster = int(selected_cluster)
    num_results = int(num_results)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    ids = clustering.getClusterLabelSublabelIds(selected_cluster,
            label, sublabel)
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

@app.route('/addClusterLabel/<project>/<dataset>/<experiment_id>/<selected_cluster>/<num_results>/<label>/<sublabel>/<label_iteration>/<label_method>/')
def addClusterLabel(project, dataset, experiment_id, selected_cluster, num_results, label, sublabel, 
        label_iteration, label_method):
    selected_cluster = int(selected_cluster)
    num_results = int(num_results)
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    clustering = Clustering.fromJson(experiment)
    clustering.addClusterLabel(selected_cluster, num_results,
            label, sublabel, label_iteration, label_method)
    db.commit()
    return ''

@app.route('/getClusterStats/<project>/<dataset>/<experiment_id>/')
def getClusterStats(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    experiment_label_id = experiment.experiment_label_id
    clustering = Clustering.fromJson(experiment)
    num_clusters = clustering.num_clusters 
    all_colors = colors_tools.colors(num_clusters)
    num_unknown_v   = []
    num_malicious_v = []
    num_benign_v    = []
    mysql_tools.useDatabase(cursor, project, dataset)
    for c in range(num_clusters):
        instances_in_cluster = clustering.clusters[c].instances_ids
        cluster_stats = labels_tools.getUnknownMaliciousBenignStats(
                cursor, experiment_label_id, instances_in_cluster)
        num_unknown_v.append(cluster_stats['unknown'])
        num_malicious_v.append(cluster_stats['malicious'])
        num_benign_v.append(cluster_stats['benign'])
    labels = ['c_' + str(c) for c in range(num_clusters)]
    #labels = [clustering.getClusterLabel(c) for c in range(num_clusters)]
    barplot = BarPlot(labels)
    barplot.addDataset(num_unknown_v, 'black', 'unknown')
    barplot.addDataset(num_malicious_v, 'red', 'malicious')
    barplot.addDataset(num_benign_v, 'green', 'benign')
    return jsonify(barplot.barplot)

@app.route('/getClustersColors/<num_clusters>/')
def getClustersColors(num_clusters):
    return jsonify({'colors': colors_tools.colors(num_clusters)})
