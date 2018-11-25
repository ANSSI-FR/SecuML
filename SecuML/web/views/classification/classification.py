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

from SecuML.web import app, session
from SecuML.web.views.experiments import updateCurrentExperiment

from SecuML.core.tools.plots.BarPlot import BarPlot
from SecuML.core.tools.plots.PlotDataset import PlotDataset
from SecuML.core.tools import colors_tools

from SecuML.exp.classification.ClassificationExperiment \
        import ClassificationExperiment
from SecuML.exp.data.FeaturesFromExp import FeaturesFromExp
from SecuML.exp.db_tables import AlertsClusteringExpAlchemy
from SecuML.exp.db_tables import FeaturesAlchemy


@app.route('/predictionsAnalysis/<experiment_id>/<train_test>/<fold_id>/'
           '<index>/')
def predictionsAnalysis(experiment_id, train_test, fold_id, index):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template('classification/predictions.html',
                           project=experiment.exp_conf.dataset_conf.project)


@app.route('/alerts/<experiment_id>/<analysis_type>/<fold_id>/')
def displayAlerts(experiment_id, analysis_type, fold_id):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template('classification/alerts.html',
                           project=experiment.exp_conf.dataset_conf.project)


@app.route('/errors/<experiment_id>/<train_test>/<fold_id>/<error_kind>/')
def displayErrors(experiment_id, train_test, fold_id, error_kind):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template('classification/errors.html',
                           project=experiment.exp_conf.dataset_conf.project)


@app.route('/getAlertsClusteringExperimentId/<experiment_id>/')
def getAlertsClusteringExperimentId(experiment_id):
    experiment_id = int(experiment_id)
    query = session.query(AlertsClusteringExpAlchemy)
    query = query.filter(AlertsClusteringExpAlchemy.diadem_id == experiment_id)
    try:
        return str(query.one().clustering_id)
    except sqlalchemy.orm.exc.NoResultFound as e:
        return 'None'


@app.route('/getAlerts/<exp_id>/<analysis_type>/<fold_id>/')
def getAlerts(exp_id, analysis_type, fold_id):
    exp = updateCurrentExperiment(exp_id)
    directory = exp.output_dir()
    if fold_id != 'None' and fold_id != 'all':
        directory = path.join(directory, fold_id)
    filename = path.join(directory, 'alerts', 'alerts.csv')
    with open(filename, 'r') as f:
        data = pd.read_csv(f, header=0, index_col=0)
        alerts_conf = exp.exp_conf.core_conf.test_conf.alerts_conf
        num_max_alerts = alerts_conf.num_max_alerts
        alerts = list(data[['predicted_proba']].itertuples())
        if num_max_alerts < len(alerts):
            if analysis_type == 'topN':
                alerts = alerts[:num_max_alerts]
            elif analysis_type == 'random':
                alerts = random.sample(alerts, num_max_alerts)
    return jsonify({'instances': [int(alert[0]) for alert in alerts],
                    'proba': [alert[1] for alert in alerts]})


@app.route('/getPredictions/<experiment_id>/<train_test>/<fold_id>/<index>/'
           '<label>/')
def getPredictions(experiment_id, train_test, fold_id, index, label):
    experiment = updateCurrentExperiment(experiment_id)
    directory = experiment.output_dir()
    if fold_id != 'None' and fold_id != 'all':
        directory = path.join(directory, fold_id)
    directory = path.join(directory, train_test)
    filename = path.join(directory, 'predictions.csv')
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
        proba = list(data['predicted_proba'])
    return jsonify({'instances': selected_instances, 'proba': proba})


@app.route('/supervisedLearningMonitoring/<exp_id>/<train_test>/<kind>/'
           '<fold_id>/')
def supervisedLearningMonitoring(exp_id, train_test, kind, fold_id):
    directory = updateCurrentExperiment(exp_id).output_dir()
    if fold_id != 'None' and fold_id != 'all':
        directory = path.join(directory, fold_id)
    directory = path.join(directory, train_test)
    filename = kind
    if kind in ['ROC', 'false_discovery_recall_curve']:
        filename += '.png'
    else:
        filename += '.json'
    return send_file(path.join(directory, filename))


@app.route('/getTopWeightedFeatures/<exp_id>/<inst_exp_id>/<instance_id>/'
           '<size>/<fold_id>/')
def getTopWeightedFeatures(exp_id, inst_exp_id, instance_id, size, fold_id):
    if fold_id == 'all':
        return None
    instance_id = int(instance_id)
    exp = updateCurrentExperiment(exp_id)
    inst_exp = updateCurrentExperiment(inst_exp_id)
    # get the features
    features_from_exp = FeaturesFromExp(inst_exp)
    features_names, features_values = features_from_exp.get_instance(instance_id)
    features_values = [float(value) for value in features_values]
    # get the pipeline with scaler and logistic model
    experiment_dir = exp.output_dir()
    if fold_id != 'None':
        experiment_dir = path.join(experiment_dir, fold_id)
    pipeline = joblib.load(path.join(experiment_dir, 'model', 'model.out'))
    # scale the features
    scaled_values = pipeline.named_steps['scaler'].transform(np.reshape(
                                                    features_values, (1, -1)))
    weighted_values = np.multiply(scaled_values,
                                  pipeline.named_steps['model'].coef_)
    features = list(map(lambda name, value, w_value: (name, value, w_value),
                        features_names, features_values, weighted_values[0]))
    features.sort(key=lambda tup: abs(tup[2]))
    features = features[:-int(size) - 1:-1]

    features_names = [x[0] for x in features]
    features_values = [x[1] for x in features]
    features_weighted_values = [x[2] for x in features]
    labels = [str(name) for name in features_names]
    tooltips = ['%s (%.2f)' % (name, features_values[i])
                for i, name in enumerate(features_names)]
    barplot = BarPlot(labels)
    dataset = PlotDataset(features_weighted_values, None)
    dataset.set_color(colors_tools.red)
    barplot.add_dataset(dataset)
    return jsonify(barplot.to_json(tooltip_data=tooltips))

@app.route('/getTopModelFeatures/<exp_id>/<size>/<train_test>/<fold_id>/')
def getTopModelFeatures(exp_id, size, train_test, fold_id):
    exp = updateCurrentExperiment(exp_id)
    directory = exp.output_dir()
    if fold_id != 'None' and fold_id != 'all':
        directory = path.join(directory, fold_id)
    directory = path.join(directory, train_test)
    filename = path.join(directory, 'model_coefficients.csv')
    with open(filename, 'r') as f:
        coefficients_df = pd.read_csv(f, header=0, index_col=0, nrows=int(size))
        coefficients = list(coefficients_df['mean'])
        features_ids = coefficients_df.index
        tooltip_data = []
        user_ids = []
        for feature_id in features_ids:
            query = session.query(FeaturesAlchemy)
            query = query.filter(FeaturesAlchemy.id == int(feature_id))
            row = query.one()
            tooltip_data.append(row.name)
            user_ids.append(row.user_id)
        barplot = BarPlot(user_ids)
        dataset = PlotDataset(coefficients, None)
        score = exp.exp_conf.core_conf.classifier_conf.featureImportance()
        if score == 'weight':
            dataset.set_color(colors_tools.red)
        barplot.add_dataset(dataset)
        return jsonify(barplot.to_json(tooltip_data=tooltip_data))
