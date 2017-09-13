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

from flask import jsonify
import importlib

from SecuML_web.base import app, session
from SecuML_web.base.views.experiments import updateCurrentExperiment

from SecuML.Data import idents_tools
from SecuML.Experiment import experiment_db_tools

@app.route('/getInstance/<experiment_id>/<view_id>/<instance_id>/<path:ident>/')
def getInstance(experiment_id, view_id, instance_id, ident):
    try:
        if view_id == 'None':
            view_id = None
        experiment = updateCurrentExperiment(experiment_id)
        project = experiment.project
        module = importlib.import_module('SecuML_web.base.views.Projects.' + project)
        return module.getInstance(experiment, view_id, instance_id, ident)
    except IOError as e:
        app.logger.error(e)
        return 'Unable to display the instance', ident

@app.route('/getIdent/<experiment_id>/<instance_id>/')
def getIdent(experiment_id, instance_id):
    dataset_id = experiment_db_tools.getExperimentRow(session, experiment_id).dataset_id
    ident = idents_tools.getIdent(session, dataset_id, instance_id)
    return ident

@app.route('/getFeatures/<experiment_id>/<instance_id>/')
def getFeatures(experiment_id, instance_id):
    instance_id = int(instance_id)
    experiment = updateCurrentExperiment(experiment_id)
    features_names, features_values = experiment.getFeatures(instance_id)
    features = zip(features_names, features_values)
    return jsonify(features)
