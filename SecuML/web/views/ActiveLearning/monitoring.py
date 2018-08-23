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

from flask import jsonify, send_file
import json
import os.path as path

from SecuML.web import app
from SecuML.web.views.experiments import updateCurrentExperiment

from SecuML.experiments.ActiveLearning.IterationExp import IterationExp


@app.route('/getLabelsMonitoring/<experiment_id>/<iteration>/')
def getLabelsMonitoring(experiment_id, iteration):
    experiment = updateCurrentExperiment(experiment_id)
    filename = path.join(experiment.getOutputDirectory(),
                         str(iteration),
                         'labels_monitoring',
                         'labels_monitoring.json')
    with open(filename, 'r') as f:
        stats = json.load(f)
        res = {}
        res['unlabeled'] = stats['unlabeled']
        res['annotations'] = stats['global']['annotations']
        return jsonify(res)


@app.route('/activeLearningSuggestionsMonitoring/<experiment_id>/<iteration>/')
def activeLearningSuggestionsMonitoring(experiment_id, iteration):
    iteration = int(iteration)
    experiment = updateCurrentExperiment(experiment_id)
    filename = path.join(experiment.getOutputDirectory(),
                         str(iteration-1),
                         'suggestions_accuracy',
                         'labels_families_high_confidence_suggestions.png')
    return send_file(filename)


@app.route('/activeLearningModelsMonitoring/<experiment_id>/<iteration>/<train_cv_validation>/')
def activeLearningModelsMonitoring(experiment_id, iteration, train_cv_validation):
    experiment = updateCurrentExperiment(experiment_id)
    binary_multiclass = 'multiclass'
    estimator = 'accuracy'
    if 'binary' in list(experiment.conf.models_conf.keys()):
        binary_multiclass = 'binary'
        estimator = 'auc'
    directory = path.join(experiment.getOutputDirectory(),
                          str(iteration),
                          'models_performance')
    filename = '_'.join([binary_multiclass,
                         train_cv_validation,
                         estimator,
                         'monitoring.png'])
    return send_file(path.join(directory, filename), mimetype='image/png')


@app.route('/activeLearningMonitoring/<experiment_id>/<iteration>/<kind>/<sub_kind>/')
def activeLearningMonitoring(experiment_id, iteration, kind, sub_kind):
    experiment = updateCurrentExperiment(experiment_id)
    directory = path.join(experiment.getOutputDirectory(), str(iteration))
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
                             'execution_time_monitoring.png')
    try:
        return send_file(filename, mimetype='image/png')
    except FileNotFoundError:
        return 'FileNotFoundError'
