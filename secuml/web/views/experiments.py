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

from secuml.web import app, secuml_conf, session

from flask import jsonify, redirect, render_template, send_file
import operator
import os
from sqlalchemy import desc

from secuml.exp import experiment
from secuml.exp.experiment import get_project_dataset
from secuml.exp.tools.db_tables import DatasetsAlchemy
from secuml.exp.tools.db_tables import FeaturesSetsAlchemy
from secuml.exp.tools.db_tables import ExpAlchemy
from secuml.exp.tools.db_tables import ExpRelationshipsAlchemy
from secuml.exp.tools.db_tables import FeaturesAnalysisExpAlchemy


def update_curr_exp(exp_id):
    return experiment.get_factory().from_exp_id(exp_id, secuml_conf, session)


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


@app.route('/SecuML/<exp_id>/')
def getExperiment(exp_id):
    exp = update_curr_exp(exp_id)
    return render_template(exp.web_template(),
                           project=exp.exp_conf.dataset_conf.project)


@app.route('/getProjects/')
def getProjects():
    query = session.query(DatasetsAlchemy.project).distinct()
    return jsonify({'projects': [r.project for r in query.all()]})


@app.route('/getDatasets/<project>/')
def getDatasets(project):
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.project == project)
    return jsonify({'datasets': [r.dataset for r in query.all()]})


@app.route('/getConf/<exp_id>/')
def getConf(exp_id):
    project, dataset = get_project_dataset(session, exp_id)
    conf_filename = os.path.join(secuml_conf.output_data_dir, project, dataset,
                                 str(exp_id), 'conf.json')
    return send_file(conf_filename)


@app.route('/hasGroundTruth/<project>/<dataset>/')
def hasGroundTruth(project, dataset):
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.project == project)
    query = query.filter(DatasetsAlchemy.dataset == dataset)
    return query.one().ground_truth_hash is not None


@app.route('/getAllExperiments/<project>/<dataset>/')
def getAllExperiments(project, dataset):
    query = session.query(ExpAlchemy)
    query = query.join(ExpAlchemy.features_set)
    query = query.join(FeaturesSetsAlchemy.dataset)
    query = query.outerjoin(ExpAlchemy.parents)
    query = query.filter(DatasetsAlchemy.project == project)
    query = query.filter(DatasetsAlchemy.dataset == dataset)
    query = query.filter(ExpRelationshipsAlchemy.parent_id == None)
    experiments = {}
    for exp in query.all():
        if exp.kind not in experiments:
            experiments[exp.kind] = []
        experiments[exp.kind].append({'name': exp.name, 'id': exp.id})
    for k, v in experiments.items():
        t = [(x['id'], x['name']) for x in v]
        t.sort(key=operator.itemgetter(0), reverse=True)
        experiments[k] = t
    return jsonify(experiments)


@app.route('/getFeaturesAnalysisExp/<exp_id>/')
def getFeaturesAnalysisExp(exp_id):
    exp = update_curr_exp(exp_id)
    features_exp_id = None
    features_set_id = exp.exp_conf.features_conf.features_set_id
    query = exp.session.query(FeaturesAnalysisExpAlchemy)
    query = query.filter(FeaturesAnalysisExpAlchemy.features_set_id ==
                         features_set_id)
    query = query.filter(FeaturesAnalysisExpAlchemy.annotations_filename ==
                         'ground_truth.csv')
    query = query.order_by(desc(FeaturesAnalysisExpAlchemy.id))
    res = query.first()
    if res is not None:
        features_exp_id = res.id
    else:
        query = exp.session.query(FeaturesAnalysisExpAlchemy)
        query = query.filter(FeaturesAnalysisExpAlchemy.features_set_id ==
                             features_set_id)
        query = query.order_by(desc(FeaturesAnalysisExpAlchemy.id))
        res = query.first()
        if res is not None:
            features_exp_id = res.id
    return str(features_exp_id)


@app.route('/SecuML/<exp_id>/<feature>/')
def getFeaturesAnalysisExperiment(exp_id, feature):
    exp = update_curr_exp(exp_id)
    return render_template(exp.web_template(), feature={'feature': feature})
