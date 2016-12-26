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

from flask import send_file

from SecuML_web.base import app, db, cursor

from SecuML.ActiveLearning.Iteration import Iteration
from SecuML.Experiment import ExperimentFactory
from SecuML.Tools import dir_tools

@app.route('/getLabelsMonitoring/<project>/<dataset>/<experiment_id>/<iteration>/')
def getLabelsMonitoring(project, dataset, experiment_id, iteration):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    filename  = dir_tools.getExperimentOutputDirectory(experiment) + str(iteration) + '/'
    filename += 'labels_monitoring/' + 'labels_monitoring.json'
    return send_file(filename)

@app.route('/activeLearningMonitoring/<project>/<dataset>/<experiment_id>/<iteration>/<kind>/<sub_kind>/')
def activeLearningLabelMonitoring(project, dataset, experiment_id, iteration, kind, sub_kind):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id, db, cursor)
    active_learning = Iteration(None, experiment, None, None, None, None,
            iteration_number = int(iteration))
    directory = active_learning.output_directory
    if kind == 'labels':
        filename  = directory + 'labels_monitoring/'
        filename += 'iteration' + '_' + sub_kind + '.png'
    if kind == 'sublabels':
        filename = directory + 'labels_monitoring/' + 'sublabels_monitoring.png'
    if kind == 'clustering':
        filename  = directory + 'clustering_evaluation/'
        filename += sub_kind + '_monitoring.png'
    if kind == 'validation':
        filename  = directory
        filename += sub_kind + '_validation_monitoring.png'
    if kind == 'time':
        filename  = directory
        filename += 'execution_time_monitoring.png'
    return send_file(filename, mimetype='image/png')
