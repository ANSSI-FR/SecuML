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

from flask import render_template, send_file, jsonify
import numpy as np
import os.path as path
import pandas as pd
import random
from sklearn.externals import joblib
import sqlalchemy

from secuml.web import app, session
from secuml.web.views.experiments import update_curr_exp

from secuml.core.tools.plots.barplot import BarPlot
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.core.tools.color import red

from secuml.exp.diadem import DiademExp
from secuml.exp.data.features import FeaturesFromExp
from secuml.exp.tools.db_tables import DiademExpAlchemy
from secuml.exp.tools.db_tables import ExpAlchemy
from secuml.exp.tools.db_tables import ExpRelationshipsAlchemy

TOP_N_ALERTS = 100


def db_row_to_json(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


@app.route('/getDiademChildExp/<diadem_exp_id>/<child_type>/<fold_id>/')
def getDiademChildExp(diadem_exp_id, child_type, fold_id):
    fold_id = None if fold_id == 'None' else int(fold_id)
    query = session.query(DiademExpAlchemy)
    if child_type != 'cv':
        query = query.join(DiademExpAlchemy.exp)
        query = query.join(ExpAlchemy.parents)
        query = query.filter(ExpRelationshipsAlchemy.parent_id == diadem_exp_id)
    else:
        query = query.filter(DiademExpAlchemy.exp_id == diadem_exp_id)
    query = query.filter(DiademExpAlchemy.type == child_type)
    query = query.filter(DiademExpAlchemy.fold_id == fold_id)
    return jsonify(db_row_to_json(query.one()))


@app.route('/getDiademExp/<exp_id>/')
def getDiademExp(exp_id):
    query = session.query(DiademExpAlchemy)
    query = query.filter(DiademExpAlchemy.exp_id == exp_id)
    return jsonify(db_row_to_json(query.one()))


@app.route('/predictionsAnalysis/<train_exp_id>/<index>/')
def predictionsAnalysis(train_exp_id, index):
    exp = update_curr_exp(train_exp_id)
    return render_template('diadem/predictions.html',
                           project=exp.exp_conf.dataset_conf.project)


@app.route('/alerts/<exp_id>/<analysis_type>/')
def displayAlerts(exp_id, analysis_type):
    experiment = update_curr_exp(exp_id)
    return render_template('diadem/alerts.html',
                           project=experiment.exp_conf.dataset_conf.project)


@app.route('/errors/<exp_id>/<error_kind>/')
def displayErrors(exp_id, error_kind):
    experiment = update_curr_exp(exp_id)
    return render_template('diadem/errors.html',
                           project=experiment.exp_conf.dataset_conf.project)


@app.route('/getAlertsClusteringExpId/<test_exp_id>/')
def getAlertsClusteringExpId(test_exp_id):
    query = session.query(ExpRelationshipsAlchemy)
    query = query.join(ExpRelationshipsAlchemy.child)
    query = query.join(ExpAlchemy.diadem_exp)
    query = query.filter(ExpRelationshipsAlchemy.parent_id == test_exp_id)
    query = query.filter(DiademExpAlchemy.type == 'alerts')
    try:
        return str(query.one().child_id)
    except sqlalchemy.orm.exc.NoResultFound:
        return 'None'


@app.route('/getAlerts/<exp_id>/<analysis_type>/')
def getAlerts(exp_id, analysis_type):
    exp = update_curr_exp(exp_id)
    filename = path.join(exp.output_dir(), 'alerts.csv')
    with open(filename, 'r') as f:
        data = pd.read_csv(f, header=0, index_col=0)
        alerts = list(data[['predicted_proba']].itertuples())
        if TOP_N_ALERTS < len(alerts):
            if analysis_type == 'topN':
                alerts = alerts[:TOP_N_ALERTS]
            elif analysis_type == 'random':
                alerts = random.sample(alerts, TOP_N_ALERTS)
    return jsonify({'instances': [int(alert[0]) for alert in alerts],
                    'proba': [alert[1] for alert in alerts]})


@app.route('/getPredictions/<exp_id>/<index>/<label>/')
def getPredictions(exp_id, index, label):
    exp = update_curr_exp(exp_id)
    filename = path.join(exp.output_dir(), 'predictions.csv')
    index = int(index)
    min_value = index * 0.1
    max_value = (index + 1) * 0.1
    with open(filename, 'r') as f:
        data = pd.read_csv(f, header=0, index_col=0)
        selection = data.loc[:, 'predicted_proba'] >= min_value
        data = data.loc[selection, :]
        selection = data.loc[:, 'predicted_proba'] <= max_value
        data = data.loc[selection, :]
        if label != 'all':
            if label == 'malicious':
                selection = data.loc[:, 'ground_truth'] == True
            elif label == 'benign':
                selection = data.loc[:, 'ground_truth'] == False
            data = data.loc[selection, :]
        selected_instances = [int(x) for x in list(data.index.values)]
    return jsonify({'instances': selected_instances,
                    'proba': list(data['predicted_proba'])})


@app.route('/supervisedLearningMonitoring/<exp_id>/<kind>/')
def supervisedLearningMonitoring(exp_id, kind):
    exp = update_curr_exp(exp_id)
    filename = kind
    if kind in ['ROC', 'false_discovery_recall_curve']:
        filename += '.png'
    else:
        filename += '.json'
    return send_file(path.join(exp.output_dir(), filename))


@app.route('/predictionsInterpretation/<exp_id>/')
def predictionsInterpretation(exp_id):
    query = session.query(DiademExpAlchemy)
    query = query.filter(DiademExpAlchemy.exp_id == exp_id)
    # first() and not one()
    # because a train experiment can be shared by several DIADEM experiments.
    return str(query.first().predictions_interpretation)


def get_train_exp(exp_id):
    query = session.query(DiademExpAlchemy)
    query = query.filter(DiademExpAlchemy.exp_id == exp_id)
    row = query.one()
    if row.type == 'train':
        return exp_id
    elif row.type == 'test':
        fold_id = row.fold_id
        # get diadem_exp
        query = session.query(ExpRelationshipsAlchemy)
        query = query.filter(ExpRelationshipsAlchemy.child_id == exp_id)
        diadem_exp_id = query.one().parent_id
        # get train_exp
        query = session.query(DiademExpAlchemy)
        query = query.join(DiademExpAlchemy.exp)
        query = query.join(ExpAlchemy.parents)
        query = query.filter(
                ExpRelationshipsAlchemy.parent_id == diadem_exp_id)
        query = query.filter(DiademExpAlchemy.fold_id == row.fold_id)
        query = query.filter(DiademExpAlchemy.type == 'train')
        return query.one().exp_id
    else:
        assert(False)


def get_classifier(exp_id):
    train_exp_id = get_train_exp(exp_id)
    train_exp = update_curr_exp(train_exp_id)
    return joblib.load(path.join(train_exp.output_dir(), 'model.out'))


@app.route('/getTopWeightedFeatures/<exp_id>/<instance_id>/<size>/')
def getTopWeightedFeatures(exp_id, instance_id, size):
    instance_id = int(instance_id)
    classifier = get_classifier(exp_id)
    # get the features
    exp = update_curr_exp(exp_id)
    f_names, f_values = FeaturesFromExp.get_instance(exp, instance_id)
    # scale the features
    scaled_values = classifier.named_steps['scaler'].transform(np.reshape(
                                                    f_values, (1, -1)))
    weighted_values = np.multiply(scaled_values,
                                  classifier.named_steps['model'].coef_)
    features = list(map(lambda name, value, w_value: (name, value, w_value),
                        f_names, f_values, weighted_values[0]))
    features.sort(key=lambda tup: abs(tup[2]))
    features = features[:-int(size) - 1:-1]
    f_names, f_values, f_weighted = list(zip(*features))
    labels = [str(name) for name in f_names]
    tooltips = ['%s (%.2f)' % (name, f_values[i])
                for i, name in enumerate(f_names)]
    barplot = BarPlot(labels)
    dataset = PlotDataset(f_weighted, None)
    dataset.set_color(red)
    barplot.add_dataset(dataset)
    return jsonify(barplot.to_json(tooltip_data=tooltips))
