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

from SecuML.web import app, session

from flask import jsonify, redirect, render_template
import operator

from SecuML.experiments import db_tables
from SecuML.experiments import experiment_db_tools
from SecuML.experiments import ExperimentFactory


def updateCurrentExperiment(experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(experiment_id, session)
    return experiment


@app.route('/SecuML/')
def secumlMenu():
    return render_template('main_menu.html')


@app.route('/')
def secumlRootMenu():
        return redirect('/SecuML/')


@app.route('/SecuML/<project>/menu/')
def projectMenu(project):
    return render_template('project_menu.html')


@app.route('/SecuML/<project>/<dataset>/menu/')
def datasetMenu(project, dataset):
    return render_template('dataset_menu.html')


@app.route('/SecuML/<project>/<dataset>/<exp_type>/menu/')
def expMenu(project, dataset, exp_type):
    return render_template('experiments_menu.html')


@app.route('/SecuML/<experiment_id>/')
def getExperiment(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template(experiment.webTemplate(), project=experiment.project)


@app.route('/getProjects/')
def getProjects():
    projects = db_tables.getProjects(session)
    return jsonify({'projects': projects})


@app.route('/getDatasets/<project>/')
def getDatasets(project):
    datasets = db_tables.getDatasets(session, project)
    return jsonify({'datasets': datasets})


@app.route('/hasGroundTruth/<experiment_id>/')
def hasGroundTruth(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    return str(db_tables.hasGroundTruth(experiment))


@app.route('/getConf/<experiment_id>/')
def getConf(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    conf = experiment.toJson()
    conf['has_ground_truth'] = db_tables.hasGroundTruth(experiment)
    return jsonify(conf)


@app.route('/getAllExperiments/<project>/<dataset>/')
def getAllExperiments(project, dataset):
    experiments = experiment_db_tools.getAllExperiments(
        session, project, dataset)
    for k, v in experiments.items():
        t = [(x['id'], x['name']) for x in v]
        t.sort(key=operator.itemgetter(0), reverse=True)
        experiments[k] = t
    return jsonify(experiments)


@app.route('/getExperimentName/<experiment_id>/')
def getExperimentName(experiment_id):
    return experiment_db_tools.getExperimentName(session, experiment_id)


@app.route('/getDescriptiveStatsExp/<experiment_id>/')
def getDescriptiveStatsExp(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    return str(experiment_db_tools.getDescriptiveStatsExp(experiment.session, experiment))


@app.route('/SecuML/<experiment_id>/<feature>/')
def getDescriptiveStatsExperiment(experiment_id, feature):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template(experiment.webTemplate(), feature={'feature': feature})
