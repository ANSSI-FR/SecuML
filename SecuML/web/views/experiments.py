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

from SecuML.web import app, secuml_conf, session

from flask import jsonify, redirect, render_template, send_file
import operator
import os

from SecuML.exp import db_tables
from SecuML.exp.tools import db_tools
from SecuML.exp import ExperimentFactory


def updateCurrentExperiment(experiment_id):
    return ExperimentFactory.getFactory().from_exp_id(experiment_id,
                                                      secuml_conf, session)


@app.route('/SecuML/')
def secumlMenu():
    return render_template('menus/main.html')


@app.route('/')
def secumlRootMenu():
        return redirect('/SecuML/')


@app.route('/SecuML/<project>/menu/')
def projectMenu(project):
    return render_template('menus/projects.html')


@app.route('/SecuML/<project>/<dataset>/menu/')
def datasetMenu(project, dataset):
    return render_template('menus/datasets.html')


@app.route('/SecuML/<experiment_id>/')
def getExperiment(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template(experiment.webTemplate(),
                           project=experiment.exp_conf.dataset_conf.project)


@app.route('/getProjects/')
def getProjects():
    projects = db_tables.getProjects(session)
    return jsonify({'projects': projects})


@app.route('/getDatasets/<project>/')
def getDatasets(project):
    datasets = db_tables.getDatasets(session, project)
    return jsonify({'datasets': datasets})


@app.route('/getConf/<exp_id>/')
def getConf(exp_id):
    project, dataset = db_tools.getProjectDataset(session, exp_id)
    conf_filename = os.path.join(secuml_conf.output_data_dir, project, dataset,
                                 str(exp_id), 'conf.json')
    return send_file(conf_filename)

@app.route('/getAllExperiments/<project>/<dataset>/')
def getAllExperiments(project, dataset):
    experiments = db_tools.getAllExperiments(session, project, dataset)
    for k, v in experiments.items():
        t = [(x['id'], x['name']) for x in v]
        t.sort(key=operator.itemgetter(0), reverse=True)
        experiments[k] = t
    return jsonify(experiments)


@app.route('/getExperimentName/<experiment_id>/')
def getExperimentName(experiment_id):
    return db_tools.getExperimentName(session, experiment_id)


@app.route('/getFeaturesAnalysisExp/<experiment_id>/')
def getFeaturesAnalysisExp(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    return str(db_tools.getFeaturesAnalysisExp(experiment.session, experiment))


@app.route('/SecuML/<experiment_id>/<feature>/')
def getFeaturesAnalysisExperiment(experiment_id, feature):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template(experiment.webTemplate(),
                           feature={'feature': feature})
