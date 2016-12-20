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

from SecuML_web.base import app, db, cursor

from flask import jsonify, render_template
import sys

from SecuML.Tools import mysql_tools
from SecuML.Data import labels_tools
from SecuML.Experiment import experiment_db_tools
from SecuML.Experiment import ExperimentFactory

@app.route('/SecuML/<project>/<dataset>/<exp_type>/menu/')
def expMenu(project, dataset, exp_type):
    return render_template('experiments_menu.html')

@app.route('/SecuML/<project>/<dataset>/<experiment_id>/')
def getExperiment(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id, db, cursor)
    return render_template(experiment.webTemplate(), project = project)

@app.route('/getExperimentsNames/<project>/<dataset>/<exp_kind>/')
def getExperimentsNames(project, dataset, exp_kind):
    db.commit()
    mysql_tools.useDatabase(cursor, project, dataset)
    experiments = experiment_db_tools.getExperiments(cursor, exp_kind)
    experience_dict = {}
    for e in experiments:
        experience_dict[e] = experiment_db_tools.getExperimentId(
                cursor, e)
    return jsonify(experience_dict)

@app.route('/getExperimentName/<project>/<dataset>/<experiment_id>/')
def getExperimentName(project, dataset, experiment_id):
    db.commit()
    mysql_tools.useDatabase(cursor, project, dataset)
    return experiment_db_tools.getExperimentName(cursor, experiment_id)

@app.route('/getExperimentId/<project>/<dataset>/<experiment_name>/')
def getExperimentId(project, dataset, experiment_name):
    db.commit()
    mysql_tools.useDatabase(cursor, project, dataset)
    return str(experiment_db_tools.getExperimentId(
        cursor, experiment_name))

@app.route('/getExperimentLabelId/<project>/<dataset>/<experiment_id>/')
def getExperimentLabelId(project, dataset, experiment_id):
    db.commit()
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id, db, cursor)
    experiment_label_id = str(experiment.experiment_label_id)
    return experiment_label_id

@app.route('/getChildren/<project>/<dataset>/<experiment_id>/')
def getChildren(project, dataset, experiment_id):
    db.commit()
    mysql_tools.useDatabase(cursor, project, dataset)
    return ' '.join(map(str, experiment_db_tools.getChildren(cursor, experiment_id)))

@app.route('/hasTrueLabels/<project>/<dataset>/')
def hasTrueLabels(project, dataset):
    mysql_tools.useDatabase(cursor, project, dataset)
    has_true_labels = labels_tools.hasTrueLabels(cursor)
    return str(has_true_labels)

@app.route('/getConf/<project>/<dataset>/<experiment_id>/')
def getConf(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    conf = experiment.toJson()
    mysql_tools.useDatabase(cursor, project, dataset)
    conf['has_true_labels'] = labels_tools.hasTrueLabels(cursor)
    return jsonify(conf)

@app.route('/getValidationConf/<project>/<dataset>/<experiment_id>/')
def getValidationConf(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    return jsonify(experiment.supervised_learning_conf.test_conf.toJson())
