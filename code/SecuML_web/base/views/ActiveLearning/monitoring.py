## SecuML
## Copyright (C) 2016-2017  ANSSI
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

from flask import send_file

from SecuML_web.base import app
from SecuML_web.base.views.experiments import updateCurrentExperiment

from SecuML.ActiveLearning.Iteration import Iteration

@app.route('/getLabelsMonitoring/<experiment_id>/<iteration>/')
def getLabelsMonitoring(experiment_id, iteration):
    experiment = updateCurrentExperiment(experiment_id)
    filename  = experiment.getOutputDirectory() + str(iteration) + '/'
    filename += 'labels_monitoring/labels_monitoring.json'
    return send_file(filename)

@app.route('/activeLearningSuggestionsMonitoring/<experiment_id>/<iteration>/')
def activeLearningSuggestionsMonitoring(experiment_id, iteration):
    experiment = updateCurrentExperiment(experiment_id)
    filename  = experiment.getOutputDirectory() + str(int(iteration) - 1) + '/'
    filename += 'suggestions_accuracy/'
    filename += 'labels_families'
    filename += '_high_confidence_suggestions.png'
    return send_file(filename)

@app.route('/activeLearningModelsMonitoring/<experiment_id>/<iteration>/<train_cv_validation>/')
def activeLearningModelsMonitoring(experiment_id, iteration, train_cv_validation):
    experiment = updateCurrentExperiment(experiment_id)
    active_learning = Iteration(experiment, int(iteration))
    binary_multiclass = 'multiclass'
    estimator = 'accuracy'
    if 'binary' in experiment.conf.models_conf.keys():
        binary_multiclass = 'binary'
        estimator = 'auc'
    directory = active_learning.output_directory
    filename  = directory
    filename += 'models_performance/'
    filename += binary_multiclass + '_' + train_cv_validation + '_' + estimator + '_monitoring.png'
    return send_file(filename, mimetype='image/png')

@app.route('/activeLearningMonitoring/<experiment_id>/<iteration>/<kind>/<sub_kind>/')
def activeLearningMonitoring(experiment_id, iteration, kind, sub_kind):
    experiment = updateCurrentExperiment(experiment_id)
    active_learning = Iteration(experiment, int(iteration))
    directory = active_learning.output_directory
    if kind == 'labels':
        filename  = directory + 'labels_monitoring/'
        filename += 'iteration' + '_' + sub_kind + '.png'
    if kind == 'families':
        filename = directory + 'labels_monitoring/' + 'families_monitoring.png'
    if kind == 'clustering':
        filename  = directory + 'clustering_evaluation/'
        filename += sub_kind + '_monitoring.png'
    if kind == 'time':
        filename  = directory
        filename += 'execution_time_monitoring.png'
    return send_file(filename, mimetype='image/png')
