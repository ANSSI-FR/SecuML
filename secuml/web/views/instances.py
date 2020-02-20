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

from flask import jsonify
import importlib

from secuml.web import app, session
from secuml.web.views.experiments import update_curr_exp

from secuml.exp.data import idents_tools
from secuml.exp.data.features import FeaturesFromExp
from secuml.exp.tools.db_tables import DatasetsAlchemy
from secuml.exp.tools.db_tables import FeaturesSetsAlchemy
from secuml.exp.tools.db_tables import InstancesAlchemy
from secuml.exp.tools.db_tables import ExpAlchemy


@app.route('/getInstance/<exp_id>/<view_id>/<instance_id>/')
def getInstance(exp_id, view_id, instance_id):
    try:
        if view_id == 'None':
            view_id = None
        experiment = update_curr_exp(exp_id)
        dataset_id = experiment.exp_conf.dataset_conf.dataset_id
        ident, user_id = idents_tools.get_ident(session, dataset_id,
                                                instance_id)
        project = experiment.exp_conf.dataset_conf.project
        module = importlib.import_module('secuml.web.views.projects.%s'
                                         % project)
        return module.get_instance(experiment, view_id, user_id, ident)
    except ImportError as e:
        app.logger.error(str(e))
        app.logger.error('Please create the project file "%s.py" in '
                         'secuml/web/views/projects/' % project)
        return 'Unable to display the instance', ident


@app.route('/getIdent/<exp_id>/<instance_id>/')
def getIdent(exp_id, instance_id):
    query = session.query(InstancesAlchemy)
    query = query.join(InstancesAlchemy.dataset)
    query = query.join(DatasetsAlchemy.features)
    query = query.join(FeaturesSetsAlchemy.experiments)
    query = query.filter(ExpAlchemy.id == exp_id)
    query = query.filter(InstancesAlchemy.id == instance_id)
    res = query.one()
    return jsonify({'ident': res.ident, 'user_id': res.user_instance_id})


@app.route('/getFeatures/<exp_id>/<instance_id>/')
def getFeatures(exp_id, instance_id):
    instance_id = int(instance_id)
    experiment = update_curr_exp(exp_id)
    f_names, _, f_values = FeaturesFromExp.get_instance(experiment,
                                                        instance_id)
    return jsonify({f_names[i]: v for i, v in enumerate(f_values)})
