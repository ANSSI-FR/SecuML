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

from flask import jsonify, send_file
import json
import os.path as path

from secuml.web import app
from secuml.web.views.experiments import update_curr_exp


@app.route('/getLabelsMonitoring/<exp_id>/<iteration>/')
def getLabelsMonitoring(exp_id, iteration):
    experiment = update_curr_exp(exp_id)
    filename = path.join(experiment.output_dir(),
                         str(iteration),
                         'labels_monitoring',
                         'labels_monitoring.json')
    with open(filename, 'r') as f:
        stats = json.load(f)
        res = {}
        res['unlabeled'] = stats['unlabeled']
        res['annotations'] = stats['global']['annotations']
        return jsonify(res)


@app.route('/activeLearningSuggestionsMonitoring/<exp_id>/<iteration>/')
def activeLearningSuggestionsMonitoring(exp_id, iteration):
    iteration = int(iteration)
    experiment = update_curr_exp(exp_id)
    filename = path.join(experiment.output_dir(),
                         str(iteration-1),
                         'suggestions_accuracy',
                         'labels_families_high_confidence_suggestions.png')
    return send_file(filename)


@app.route('/activeLearningModelsMonitoring/<exp_id>/<iter>/<train_test>/')
def activeLearningModelsMonitoring(exp_id, iter, train_test):
    experiment = update_curr_exp(exp_id)
    directory = path.join(experiment.output_dir(), str(iter), 'model_perf')
    filename = '%s.png' % train_test
    return send_file(path.join(directory, filename), mimetype='image/png')


@app.route('/activeLearningMonitoring/<exp_id>/<iteration>/<kind>/<sub_kind>/')
def activeLearningMonitoring(exp_id, iteration, kind, sub_kind):
    experiment = update_curr_exp(exp_id)
    directory = path.join(experiment.output_dir(), str(iteration))
    if kind == 'labels':
        filename = path.join(directory,
                             'labels_monitoring',
                             'iteration' + '_' + sub_kind + '.png')
    if kind == 'families':
        filename = path.join(directory,
                             'labels_monitoring',
                             'families_monitoring.png')
    if kind == 'clustering':
        filename = path.join(directory,
                             'clustering_evaluation',
                             sub_kind + '_monitoring.png')
    if kind == 'time':
        filename = path.join(directory,
                             'execution_times.png')
    try:
        return send_file(filename, mimetype='image/png')
    except FileNotFoundError:
        return 'FileNotFoundError'
