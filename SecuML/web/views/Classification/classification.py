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

from flask import render_template, send_file, jsonify
import numpy as np
import pandas as pd
import random
from sklearn.externals import joblib

from SecuML.web import app, session
from SecuML.web.views.experiments import updateCurrentExperiment

from SecuML.core.Data import labels_tools
from SecuML.core.Tools.Plots.BarPlot import BarPlot
from SecuML.core.Tools.Plots.PlotDataset import PlotDataset
from SecuML.core.Tools import colors_tools
from SecuML.core.Tools import matrix_tools

from SecuML.experiments import ExperimentFactory
from SecuML.experiments.Classification.ClassificationExperiment import ClassificationExperiment


@app.route('/predictionsAnalysis/<experiment_id>/<train_test>/<fold_id>/<index>/')
def predictionsAnalysis(experiment_id, train_test, fold_id, index):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template('Classification/predictions.html', project=experiment.project)


@app.route('/alerts/<experiment_id>/<analysis_type>/')
def displayAlerts(experiment_id, analysis_type):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template('Classification/alerts.html', project=experiment.project)


@app.route('/familiesPerformance/<experiment_id>/<train_test>/')
def displayFamiliesPerformance(experiment_id, train_test):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template('Classification/families_performance.html', project=experiment.project)


@app.route('/errors/<experiment_id>/<train_test>/<fold_id>/')
def displayErrors(experiment_id, train_test, fold_id):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template('Classification/errors.html', project=experiment.project)


@app.route('/getTestExperimentId/<experiment_id>/')
def getTestExperimentId(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    with open(experiment.getOutputDirectory() + 'test_experiment.txt', 'r') as f:
        test_experiment_id = f.readline()
        return test_experiment_id


@app.route('/getAlertsClusteringExperimentId/<experiment_id>/')
def getAlertsClusteringExperimentId(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    filename = experiment.getOutputDirectory()
    filename += 'grouping.json'
    return send_file(filename)


@app.route('/getAlerts/<experiment_id>/<analysis_type>/')
def getAlerts(experiment_id, analysis_type):
    experiment = updateCurrentExperiment(experiment_id)
    filename = experiment.getOutputDirectory()
    filename += 'alerts.csv'
    with open(filename, 'r') as f:
        data = pd.read_csv(f, header=0, index_col=0)
        num_max_alerts = experiment.conf.test_conf.alerts_conf.num_max_alerts
        alerts = list(data[['predicted_proba']].itertuples())
        if num_max_alerts < len(alerts):
            if analysis_type == 'topN':
                alerts = alerts[:num_max_alerts]
            elif analysis_type == 'random':
                alerts = random.sample(alerts, num_max_alerts)
    ids = [int(alert[0]) for alert in alerts]
    alerts = {str(k): v for k, v in dict(alerts).items()}
    return jsonify({'instances': ids, 'proba': dict(alerts)})


@app.route('/getPredictions/<experiment_id>/<train_test>/<fold_id>/<index>/')
def getPredictions(experiment_id, train_test, fold_id, index):
    experiment = updateCurrentExperiment(experiment_id)
    filename = experiment.getOutputDirectory()
    if fold_id != 'None' and fold_id != 'all':
        filename += fold_id + '/'
    filename += train_test + '/predictions.csv'
    index = int(index)
    min_value = index * 0.1
    max_value = (index + 1) * 0.1
    with open(filename, 'r') as f:
        data = pd.read_csv(f, header=0, index_col=0)
        selection = data.loc[:, 'predicted_proba'] >= min_value
        data = data.loc[selection, :]
        selection = data.loc[:, 'predicted_proba'] <= max_value
        data = data.loc[selection, :]
        selected_instances = [int(x) for x in list(data.index.values)]
        proba = list(data['predicted_proba'])
    return jsonify({'instances': selected_instances, 'proba': proba})


@app.route('/supervisedLearningMonitoring/<experiment_id>/<train_test>/<kind>/<fold_id>/')
def supervisedLearningMonitoring(experiment_id, train_test, kind, fold_id):
    experiment = updateCurrentExperiment(experiment_id)
    filename = experiment.getOutputDirectory()
    if fold_id != 'None' and fold_id != 'all':
        filename += fold_id + '/'
    filename += train_test + '/'
    filename += kind
    if kind == 'ROC':
        filename += '.png'
    else:
        filename += '.json'
    return send_file(filename)


@app.route('/getFamiliesPerformance/<experiment_id>/<train_test>/<label>/<threshold>/')
def getFamiliesPerformance(experiment_id, train_test, label, threshold):
    experiment = updateCurrentExperiment(experiment_id)
    filename = experiment.getOutputDirectory() + train_test + '/families/'
    if label == labels_tools.MALICIOUS:
        filename += 'tp_'
        tp_fp = 'Detection Rate'
    elif label == labels_tools.BENIGN:
        filename += 'fp_'
        tp_fp = 'False Positive Rate'
    filename += 'families_thresholds.csv'
    with open(filename, 'r') as f:
        perf = pd.read_csv(f, header=0, index_col=0)
        families = list(perf.columns.values[:-1])
        threshold = float(threshold) / 100
        thresholds = list(perf.index[:-1])
        threshold_value = min(enumerate(thresholds),
                              key=lambda x: abs(x[1] - threshold))[1]
        perf = list(perf.loc[threshold_value])
        barplot = BarPlot(families)
        barplot.addDataset(PlotDataset(perf, tp_fp))
    return jsonify(barplot.toJson())

@app.route('/getSupervisedValidationConf/<experiment_id>/')
def getSupervisedValidationConf(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    return jsonify(experiment.conf.test_conf.toJson())

@app.route('/getTopWeightedFeatures/<experiment_id>/<inst_exp_id>/<instance_id>/<size>/<fold_id>/')
def getTopWeightedFeatures(experiment_id, inst_exp_id, instance_id, size, fold_id):
    if fold_id == 'all':
        return None
    instance_id = int(instance_id)
    exp = ExperimentFactory.getFactory().fromJson(experiment_id, session)
    validation_experiment = ExperimentFactory.getFactory().fromJson(inst_exp_id, session)
    # get the features
    features_names, features_values = validation_experiment.getFeatures(
        instance_id)
    features_values = [float(value) for value in features_values]
    # get the pipeline with scaler and logistic model
    experiment_dir = exp.getOutputDirectory()
    if fold_id != 'None':
        experiment_dir += fold_id + '/'
    pipeline = joblib.load(experiment_dir + 'model/model.out')
    # scale the features
    scaled_values = pipeline.named_steps['scaler'].transform(
        np.reshape(features_values, (1, -1)))
    weighted_values = np.multiply(
        scaled_values, pipeline.named_steps['model'].coef_)
    features = list(map(lambda name, value, w_value: (name, value, w_value),
                        features_names, features_values, weighted_values[0]))
    features.sort(key=lambda tup: abs(tup[2]))
    features = features[:-int(size) - 1:-1]

    features_names = [x[0] for x in features]
    features_values = [x[1] for x in features]
    features_weighted_values = [x[2] for x in features]

    max_length = max([len(f) for f in features_names])
    if max_length > 30:
        labels = [str(i) for i in range(len(features_names))]
        tooltips = [features_names[i] +
                    ' (' + str(features_values[i]) + ')' for i in range(len(features_names))]
    else:
        labels = features_names
        tooltips = features_values
    barplot = BarPlot(labels)
    dataset = PlotDataset(features_weighted_values, None)
    dataset.setColor(colors_tools.red)
    barplot.addDataset(dataset)
    return jsonify(barplot.toJson(tooltip_data=tooltips))

@app.route('/getTopModelFeatures/<experiment_id>/<size>/<train_test>/<fold_id>/')
def getTopModelFeatures(experiment_id, size, train_test, fold_id):
    size = int(size)
    exp = ExperimentFactory.getFactory().fromJson(experiment_id, session)
    filename = exp.getOutputDirectory()
    if fold_id != 'None' and fold_id != 'all':
        filename += fold_id + '/'
    filename += train_test + '/'
    filename += 'model_coefficients.csv'
    with open(filename, 'r') as f:
        coefficients_df = pd.read_csv(f, header=0, index_col=0)
        model_coefficients = list(coefficients_df['mean'])
        features_names = list(map(str, coefficients_df.index))
        coefficients = list(map(lambda name, coef: (name, coef),
                                features_names, model_coefficients))
        coefficients.sort(key=lambda tup: abs(tup[1]))
        coefficients = coefficients[:-size - 1:-1]

        coefficients_names = [coef[0] for coef in coefficients]
        coefficients_values = [coef[1] for coef in coefficients]
        max_length = max([len(coef) for coef in coefficients_names])

        if max_length > 30:
            coefficients_ids = [str(i) for i in range(len(coefficients_names))]
            coefficients_names = [name.replace(
                ' WHERE', '\nWHERE') for name in coefficients_names]
            barplot = BarPlot(coefficients_ids)
            dataset = PlotDataset(coefficients_values, None)
            if exp.conf.featureImportance() == 'weight':
                dataset.setColor(colors_tools.red)
            barplot.addDataset(dataset)
            return jsonify(barplot.toJson(tooltip_data=coefficients_names))
        else:
            barplot = BarPlot(coefficients_names)
            dataset = PlotDataset(coefficients_values, None)
            if exp.conf.featureImportance() == 'weight':
                dataset.setColor(colors_tools.red)
            barplot.addDataset(dataset)
            return jsonify(barplot.toJson())
