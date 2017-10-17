## SecuML
## Copyright (C) 2016-2017  ANSSI
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

from flask import render_template, send_file, jsonify
import numpy as np
import pandas as pd
import random

from SecuML_web.base import app, session
from SecuML_web.base.views.experiments import updateCurrentExperiment

from SecuML.Experiment import ExperimentFactory
from SecuML.Experiment.ClassificationExperiment import ClassificationExperiment
from SecuML.Plots.BarPlot import BarPlot
from SecuML.Plots.PlotDataset import PlotDataset
from SecuML.Tools import colors_tools
from SecuML.Tools import matrix_tools

@app.route('/predictionsAnalysis/<experiment_id>/<train_test>/<index>/')
def predictionsAnalysis(experiment_id, train_test, index):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template('Classification/predictions.html', project = experiment.project)

@app.route('/alerts/<experiment_id>/<analysis_type>/')
def displayAlerts(experiment_id, analysis_type):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template('Classification/alerts.html', project = experiment.project)

@app.route('/familiesPerformance/<experiment_id>/<train_test>/')
def displayFamiliesPerformance(experiment_id, train_test):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template('Classification/families_performance.html', project = experiment.project)

@app.route('/errors/<experiment_id>/<train_test>/')
def displayErrors(experiment_id, train_test):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template('Classification/errors.html', project = experiment.project)

@app.route('/getValidationDataset/<experiment_id>/')
def getValidationDataset(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    test_conf = experiment.classification_conf.test_conf
    if test_conf.method == 'test_dataset':
        return test_conf.test_dataset
    else:
        return experiment.dataset

@app.route('/getAlertsClusteringExperimentId/<experiment_id>/')
def getAlertsClusteringExperimentId(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    filename  = experiment.getOutputDirectory()
    filename += 'grouping.json'
    return send_file(filename)

@app.route('/getAlerts/<experiment_id>/<analysis_type>/')
def getAlerts(experiment_id, analysis_type):
    experiment = updateCurrentExperiment(experiment_id)
    filename  = experiment.getOutputDirectory()
    filename += 'alerts.csv'
    with open(filename, 'r') as f:
        data = pd.read_csv(f, header = 0, index_col = 0)
        num_max_alerts = experiment.classification_conf.test_conf.alerts_conf.num_max_alerts
        alerts = list(data[['predicted_proba']].itertuples())
        if num_max_alerts < len(alerts):
            if analysis_type == 'topN':
                alerts = alerts[:num_max_alerts]
            elif analysis_type == 'random':
                alerts = random.sample(alerts, num_max_alerts)
    return jsonify({'instances': [alert[0] for alert in alerts], 'proba': dict(alerts)})

@app.route('/getPredictions/<experiment_id>/<train_test>/<index>/')
def getPredictions(experiment_id, train_test, index):
    experiment = updateCurrentExperiment(experiment_id)
    filename  = experiment.getOutputDirectory()
    filename += train_test + '/predictions.csv'
    index = int(index)
    min_value = index * 0.1
    max_value = (index+1) * 0.1
    with open(filename, 'r') as f:
        data = pd.read_csv(f, header = 0, index_col = 0)
        data = matrix_tools.extractRowsWithThresholds(data, min_value, max_value,
                                                      'predicted_proba')
        selected_instances = list(data.index.values)
        proba              = list(data['predicted_proba'])
    return jsonify({'instances': selected_instances, 'proba': proba})

@app.route('/supervisedLearningMonitoring/<experiment_id>/<train_test>/<kind>/')
def supervisedLearningMonitoring(experiment_id, train_test, kind):
    experiment = updateCurrentExperiment(experiment_id)
    filename  = experiment.getOutputDirectory() + train_test + '/'
    filename += kind
    if kind == 'ROC':
        filename += '.png'
    else:
        filename += '.json'
    return send_file(filename)

@app.route('/getFamiliesPerformance/<experiment_id>/<train_test>/<label>/<threshold>/')
def getFamiliesPerformance(experiment_id, train_test, label, threshold):
    experiment = updateCurrentExperiment(experiment_id)
    filename  = experiment.getOutputDirectory() + train_test + '/families/'
    if label == 'malicious':
        filename += 'tp_'
        tp_fp = 'Detection Rate'
    elif label == 'benign':
        filename += 'fp_'
        tp_fp = 'False Positive Rate'
    filename += 'families_thresholds.csv'
    with open(filename, 'r') as f:
        perf = pd.read_csv(f, header = 0, index_col = 0)
        families = list(perf.columns.values[:-1])
        threshold = float(threshold)/100
        thresholds = list(perf.index[:-1])
        threshold_value = min(enumerate(thresholds), key=lambda x: abs(x[1]-threshold))[1]
        perf = list(perf.loc[threshold_value])
        barplot = BarPlot(families)
        barplot.addDataset(PlotDataset(perf, tp_fp))
    return jsonify(barplot.toJson())

@app.route('/getSupervisedValidationConf/<experiment_id>/')
def getSupervisedValidationConf(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    return jsonify(experiment.classification_conf.test_conf.toJson())

@app.route('/getTopWeightedFeatures/<experiment_id>/<inst_exp_id>/<instance_id>/<size>/')
def getTopWeightedFeatures(experiment_id, inst_exp_id, instance_id, size):
    instance_id = int(instance_id)
    exp = ExperimentFactory.getFactory().fromJson(experiment_id, session)
    validation_experiment = ExperimentFactory.getFactory().fromJson(inst_exp_id, session)
    #get the features
    features_names, features_values = validation_experiment.getFeatures(instance_id)
    features_values = [float(value) for value in features_values]
    #get the pipeline with scaler and logistic model
    pipeline = exp.getModelPipeline()
    #scale the features
    scaled_values = pipeline.named_steps['scaler'].transform(np.reshape(features_values,(1, -1)))
    weighted_values = np.multiply(scaled_values, pipeline.named_steps['model'].coef_)
    features = map(lambda name, value, w_value: (name, value, w_value),
                          features_names, features_values, weighted_values[0])
    features.sort(key = lambda tup: abs(tup[2]))
    features = features[:-int(size)-1:-1]
    tooltips = [x[1] for x in features]
    barplot = BarPlot([x[0] for x in features])
    dataset = PlotDataset([x[2] for x in features], None)
    dataset.setColor(colors_tools.red)
    barplot.addDataset(dataset)
    return jsonify(barplot.toJson(tooltip_data = tooltips))

@app.route('/getTopModelFeatures/<experiment_id>/<size>/')
def getTopModelFeatures(experiment_id, size):
    size = int(size)
    exp = ExperimentFactory.getFactory().fromJson(experiment_id, session)
    model_coefficients = exp.getTopFeatures()
    features_names = exp.getFeaturesNames()
    coefficients = map(lambda name, coef: (name, coef),
                       features_names, model_coefficients)
    coefficients.sort(key = lambda tup: abs(tup[1]))
    coefficients = coefficients[:-size-1:-1]
    barplot = BarPlot([x[0] for x in coefficients])
    dataset = PlotDataset([x[1] for x in coefficients], None)
    if (exp.classification_conf.featureImportance() == 'weight'):
        dataset.setColor(colors_tools.red)
    barplot.addDataset(dataset)
    return jsonify(barplot.toJson())
