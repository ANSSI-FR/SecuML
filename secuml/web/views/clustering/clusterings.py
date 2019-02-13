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

from flask import jsonify
import random

from secuml.core.tools.color import colors
from secuml.core.tools.plots.barplot import BarPlot
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.exp.clustering.clusters import ClustersExp

from secuml.web import app
from secuml.web.views.experiments import update_curr_exp


def _random_selection(ids, num_res=None):
    if num_res is None or len(ids) <= num_res:
        return ids
    else:
        return random.sample(ids, num_res)


@app.route('/getNumElements/<exp_id>/<selected_cluster>/')
def getNumElements(exp_id, selected_cluster):
    selected_cluster = int(selected_cluster)
    experiment = update_curr_exp(exp_id)
    clustering = ClustersExp.from_json(experiment.output_dir())
    cluster = clustering.clusters[selected_cluster]
    res = {}
    res['num_elements'] = cluster.num_instances()
    return jsonify(res)


# c_e_r :
# c : center
# e : edge
# r : random
@app.route('/getClusterInstancesVisu/<exp_id>/<selected_cluster>/<c_e_r>/'
           '<num_results>/')
def getClusterInstancesVisu(exp_id, selected_cluster, c_e_r, num_results):
    num_results = int(num_results)
    selected_cluster = int(selected_cluster)
    exp = update_curr_exp(exp_id)
    clustering = ClustersExp.from_json(exp.output_dir())
    ids = {}
    ids[selected_cluster] = clustering.get_cluster_instances_visu(
                                                            selected_cluster,
                                                            num_results,
                                                            random=True)[c_e_r]
    return jsonify(ids)


@app.route('/getClustersLabels/<exp_id>/')
def getClustersLabels(exp_id):
    experiment = update_curr_exp(exp_id)
    clustering = ClustersExp.from_json(experiment.output_dir())
    # Do not consider empty clusters for visualization
    clusters = []
    for c in range(clustering.num_clusters):
        # if clustering.clusters[c].num_instances() > 0:
        clusters.append({'id': c, 'label': clustering.clusters[c].label})
    return jsonify({'clusters': clusters})


@app.route('/getClusterLabel/<exp_id>/<selected_cluster>/')
def getClusterLabel(exp_id, selected_cluster):
    selected_cluster = int(selected_cluster)
    experiment = update_curr_exp(exp_id)
    clustering = ClustersExp.from_json(experiment.output_dir())
    predicted_label = clustering.get_label(selected_cluster)
    return predicted_label


@app.route('/getClusterLabelsFamilies/<exp_id>/<cluster_id>/')
def getClusterLabelsFamilies(exp_id, cluster_id):
    cluster_id = int(cluster_id)
    experiment = update_curr_exp(exp_id)
    clustering = ClustersExp.from_json(experiment.output_dir())
    return jsonify(clustering.get_labels_families(experiment, cluster_id))


@app.route('/getClusterLabelFamilyIds/<exp_id>/<cluster_id>/<label>/'
           '<family>/<num_results>/')
def getClusterLabelFamilyIds(exp_id, cluster_id, label, family, num_results):
    cluster_id = int(cluster_id)
    num_results = int(num_results)
    exp = update_curr_exp(exp_id)
    clustering = ClustersExp.from_json(exp.output_dir())
    ids = clustering.get_labe_family_ids(exp, cluster_id, label, family)
    return jsonify({'num_ids': len(ids),
                    'ids': _random_selection(ids, num_res)})


@app.route('/getClusterStats/<exp_id>/')
def getClusterStats(exp_id):
    experiment = update_curr_exp(exp_id)
    clustering = ClustersExp.from_json(experiment.output_dir())
    num_clusters = clustering.num_clusters
    num_instances_v = []
    labels = []
    for c in range(num_clusters):
        instances_in_cluster = clustering.clusters[c].instances_ids
        num_instances = len(instances_in_cluster)
        num_instances_v.append(num_instances)
        labels.append(clustering.clusters[c].label)
    barplot = BarPlot(labels)
    dataset = PlotDataset(num_instances_v, 'Num. Instances')
    barplot.add_dataset(dataset)
    return jsonify(barplot.to_json())


@app.route('/getClustersColors/<num_clusters>/')
def getClustersColors(num_clusters):
    return jsonify({'colors': colors(num_clusters)})
