# SecuML
# Copyright (C) 2016-2019  ANSSI
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

from flask import jsonify, send_file
import json
import os.path as path
import random

from secuml.exp.projection import ProjectionExperiment  # NOQA
from secuml.exp.tools.db_tables import InstancesAlchemy

from secuml.web import app, session
from secuml.web.views.experiments import update_curr_exp

NUM_MAX_INSTANCES = 100


def get_user_instance_ids(instance_ids):
    query = session.query(InstancesAlchemy)
    query = query.filter(InstancesAlchemy.id.in_(instance_ids))
    query = query.order_by(InstancesAlchemy.id)
    return [r.user_instance_id for r in query.all()]


@app.route('/getNumComponents/<exp_id>/')
def getNumComponents(exp_id):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = 'projection_matrix.csv'
    with open(path.join(directory, filename), 'r') as f:
        header = f.readline()
        num_components = len(header.split(',')) - 1
    return str(num_components)


@app.route('/getHexBin/<exp_id>/<x>/<y>/')
def getHexBin(exp_id, x, y):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = '_'.join(['c', x, y, 'hexbin.json'])
    with open(path.join(directory, filename), 'r') as f:
        hex_bins = json.load(f)
        for hex_bin in hex_bins[1:]:
            if hex_bin['num_malicious_instances'] > NUM_MAX_INSTANCES:
                hex_bin['malicious_instances'] = random.sample(
                                                hex_bin['malicious_instances'],
                                                NUM_MAX_INSTANCES)
            if hex_bin['num_ok_instances'] > NUM_MAX_INSTANCES:
                hex_bin['ok_instances'] = random.sample(
                                                       hex_bin['ok_instances'],
                                                       NUM_MAX_INSTANCES)
            for kind in ['malicious', 'ok']:
                ids = hex_bin['%s_instances' % kind]
                ids.sort()
                hex_bin['%s_user_ids' % kind] = get_user_instance_ids(ids)
                hex_bin['%s_instances' % kind] = ids
    return jsonify(hex_bins)


@app.route('/getProjectionMatrix/<exp_id>/')
def getProjectionMatrix(exp_id):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = 'projection_matrix.csv'
    return send_file(path.join(directory, filename))


@app.route('/getExplVar/<exp_id>/')
def getExplVar(exp_id):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = 'explained_variance.csv'
    return send_file(path.join(directory, filename))


@app.route('/getCumExplVar/<exp_id>/')
def getCumExplVar(exp_id):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = 'cumuled_explained_variance.csv'
    return send_file(path.join(directory, filename))


@app.route('/getReconsErrors/<exp_id>/')
def getReconsErrors(exp_id):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = 'reconstruction_errors.csv'
    return send_file(path.join(directory, filename))
