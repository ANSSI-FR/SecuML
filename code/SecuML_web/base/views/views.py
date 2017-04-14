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

from flask import jsonify
import importlib

from SecuML_web.base import app, db, cursor

from SecuML.Data import idents_tools
from SecuML.Experiment import ExperimentFactory
from SecuML.Tools import mysql_tools

@app.route('/getInstance/<project>/<dataset>/<instance_id>/<ident>/')
def getInstance(project, dataset, instance_id, ident):
    try:
        module = importlib.import_module('SecuML_web.base.views.Projects.' + project)
        return module.getInstance(dataset, instance_id, ident)
    except IOError as e:
        app.logger.error(e)
        return 'Unable to display the instance', ident

@app.route('/getIdent/<project>/<dataset>/<instance_id>/')
def getIdent(project, dataset, instance_id):
    mysql_tools.useDatabase(cursor, project, dataset)
    ident = idents_tools.getIdent(cursor, instance_id)
    return ident

@app.route('/getFeatures/<project>/<dataset>/<experiment>/<instance_dataset>/<instance_id>/')
def getFeatures(project, dataset, experiment, instance_dataset, instance_id):
    instance_id = int(instance_id)
    mysql_tools.useDatabase(cursor, project, dataset)
    experiment_obj = ExperimentFactory.getFactory().fromJson(project, instance_dataset, experiment, db, cursor)
    features_names, features_values = experiment_obj.getFeatures(instance_id)
    features = zip(features_names, features_values)
    return jsonify(features)
