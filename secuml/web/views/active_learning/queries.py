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

from flask import jsonify, render_template, send_file
import pandas as pd
import os.path as path

from secuml.web import app, session
from secuml.web.views.experiments import update_curr_exp
from secuml.web.views.nocache import nocache

from secuml.exp.active_learning.active_learning import ActiveLearningExperiment
from secuml.exp.active_learning.rcd import RcdExperiment
from secuml.exp.tools.db_tables import IlabExpAlchemy
from secuml.exp.tools.db_tables import RcdClusteringExpAlchemy


@app.route('/getAnnotationsTypes/<exp_id>/<iteration>/')
@nocache
def getAnnotationsTypes(exp_id, iteration):
    query = session.query(IlabExpAlchemy)
    query = query.filter(IlabExpAlchemy.id == exp_id)
    query = query.filter(IlabExpAlchemy.iter == iteration)
    res = query.one()
    return jsonify({k: getattr(res, k)
                    for k in ['uncertain', 'malicious', 'benign']})


@app.route('/getRcdClusteringId/<exp_id>/<iteration>/')
def getRcdClusteringId(exp_id, iteration):
    query = session.query(RcdClusteringExpAlchemy)
    query = query.filter(RcdClusteringExpAlchemy.id == exp_id)
    query = query.filter(RcdClusteringExpAlchemy.iter == iteration)
    res = query.one()
    return jsonify({'clustering_exp_id': query.one().clustering_exp})


@app.route('/getFamiliesInstancesToAnnotate/<exp_id>/<iteration>/<predicted_label>/')
def getFamiliesInstancesToAnnotate(exp_id, iteration, predicted_label):
    experiment = update_curr_exp(exp_id)
    filename = path.join(experiment.output_dir(),
                         str(iteration),
                         'toannotate_' + predicted_label + '.json')
    return send_file(filename)


@app.route('/getInstancesToAnnotate/<exp_id>/<iteration>/<predicted_label>/')
def getInstancesToAnnotate(exp_id, iteration, predicted_label):
    experiment = update_curr_exp(exp_id)
    if predicted_label == 'None':
        filename = 'toannotate.csv'
    else:
        filename = 'toannotate_%s.csv' % predicted_label
    filename = path.join(experiment.output_dir(),
                         iteration,
                         filename)
    df = pd.read_csv(filename)
    queries = [int(x) for x in df.instance_id]
    return jsonify({'instances': queries})


@app.route('/individualAnnotations/<exp_id>/<iteration>/')
def individualAnnotations(exp_id, iteration):
    experiment = update_curr_exp(exp_id)
    return render_template('active_learning/individual_annotations.html',
                           project=experiment.exp_conf.dataset_conf.project)


@app.route('/ilabAnnotations/<exp_id>/<iteration>/')
def ilabAnnotations(exp_id, iteration):
    experiment = update_curr_exp(exp_id)
    return render_template('active_learning/ilab_annotations.html',
                           project=experiment.exp_conf.dataset_conf.project)


@app.route('/rcdAnnotations/<exp_id>/<iteration>/')
def rcdAnnotations(exp_id, iteration):
    experiment = update_curr_exp(exp_id)
    return render_template('active_learning/rcd_annotations.html',
                           project=experiment.exp_conf.dataset_conf.project)
