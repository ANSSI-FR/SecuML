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
import importlib

from SecuML.web import app, session
from SecuML.web.views.experiments import updateCurrentExperiment

from SecuML.exp.data import idents_tools
from SecuML.exp.data.FeaturesFromExp import FeaturesFromExp
from SecuML.exp.tools import db_tools


@app.route('/getInstance/<experiment_id>/<view_id>/<instance_id>/')
def getInstance(experiment_id, view_id, instance_id):
    try:
        if view_id == 'None':
            view_id = None
        experiment = updateCurrentExperiment(experiment_id)
        dataset_id = experiment.exp_conf.dataset_conf.dataset_id
        ident, user_id = idents_tools.getIdent(session, dataset_id, instance_id)
        project = experiment.exp_conf.dataset_conf.project
        module = importlib.import_module('SecuML.web.views.projects.' + project)
        return module.getInstance(experiment, view_id, user_id, ident)
    except ImportError as e:
        app.logger.error(str(e))
        app.logger.error('Please create the project file "%s.py" in '
                         'SecuML/web/views/projects/' % project)
        return 'Unable to display the instance', ident


@app.route('/getIdent/<inst_exp_id>/<instance_id>/')
def getIdent(inst_exp_id, instance_id):
    inst_exp_row = db_tools.getExperimentRow(session, inst_exp_id)
    dataset_id = inst_exp_row.dataset_id
    ident, user_id = idents_tools.getIdent(session, dataset_id, instance_id)
    return jsonify({'ident': ident, 'user_id': user_id})


@app.route('/getFeatures/<experiment_id>/<instance_id>/')
def getFeatures(experiment_id, instance_id):
    instance_id = int(instance_id)
    experiment = updateCurrentExperiment(experiment_id)
    features_from_exp = FeaturesFromExp(experiment)
    features_names, features_values = features_from_exp.get_instance(instance_id)
    features = {features_names[i]: v for i, v in enumerate(features_values)}
    return jsonify(features)
