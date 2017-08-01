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

from SecuML_web.base import app, db, cursor

from SecuML.Experiment import ExperimentFactory
from SecuML.Experiment.ClassificationExperiment import ClassificationExperiment
from SecuML.Plots.BarPlot import BarPlot
from SecuML.Plots.PlotDataset import PlotDataset
from SecuML.Tools import colors_tools
from SecuML.Tools import dir_tools
from SecuML.Tools import matrix_tools

def getDir(project, dataset, experiment_id):
    exp = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
                                                  db, cursor)
    return dir_tools.getExperimentOutputDirectory(exp)

@app.route('/predictionsAnalysis/<project>/<dataset>/<experiment>/<train_test>/<index>/')
def predictionsAnalysis(project, dataset, experiment, train_test, index):
    return render_template('Classification/predictions.html', project = project)

@app.route('/alerts/<project>/<dataset>/<experiment>/<analysis_type>/')
def displayAlerts(project, dataset, experiment, analysis_type):
    return render_template('Classification/alerts.html', project = project)

@app.route('/familiesPerformance/<project>/<dataset>/<experiment>/<train_test>/')
def displayFamiliesPerformance(project, dataset, experiment, train_test):
    return render_template('Classification/families_performance.html', project = project)

@app.route('/errors/<project>/<dataset>/<experiment>/<train_test>/<experiment_label_id>/')
def displayErrors(project, dataset, experiment, train_test, experiment_label_id):
    return render_template('Classification/errors.html', project = project)

@app.route('/getValidationDataset/<project>/<dataset>/<experiment_id>/')
def getValidationDataset(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    test_conf = experiment.classification_conf.test_conf
    if test_conf.method == 'test_dataset':
        return test_conf.test_dataset
    else:
        return dataset

@app.route('/getAlertsClusteringExperimentId/<project>/<dataset>/<experiment_id>/')
def getAlertsClusteringExperimentId(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    filename  = dir_tools.getExperimentOutputDirectory(experiment)
    filename += 'grouping.json'
    return send_file(filename)

@app.route('/getAlerts/<project>/<dataset>/<experiment_id>/<analysis_type>/')
def getAlerts(project, dataset, experiment_id, analysis_type):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
                                                         db, cursor)
    filename  = dir_tools.getExperimentOutputDirectory(experiment)
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

@app.route('/getPredictions/<project>/<dataset>/<experiment_id>/<train_test>/<index>/')
def getPredictions(project, dataset, experiment_id, train_test, index):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
                                                         db, cursor)
    filename  = dir_tools.getExperimentOutputDirectory(experiment)
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

@app.route('/supervisedLearningMonitoring/<project>/<dataset>/<experiment>/<train_test>/<kind>/')
def supervisedLearningMonitoring(project, dataset, experiment, train_test, kind):
    filename  = getDir(project, dataset, experiment) + train_test + '/'
    filename += kind
    if kind == 'ROC':
        filename += '.png'
    else:
        filename += '.json'
    return send_file(filename)

@app.route('/getFamiliesPerformance/<project>/<dataset>/<experiment>/<train_test>/<label>/<threshold>/')
def getFamiliesPerformance(project, dataset, experiment, train_test, label, threshold):
    filename  = getDir(project, dataset, experiment) + train_test + '/families/'
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
        dataset = PlotDataset(perf, tp_fp)
        barplot.addDataset(PlotDataset(perf, tp_fp))
    return jsonify(barplot.toJson())

@app.route('/getSupervisedValidationConf/<project>/<dataset>/<experiment_id>/')
def getSupervisedValidationConf(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    return jsonify(experiment.classification_conf.test_conf.toJson())

@app.route('/getTopWeightedFeatures/<project>/<dataset>/<experiment>/<instance_dataset>/<inst_exp_id>/<instance_id>/<size>/')
def getTopWeightedFeatures(project, dataset, experiment, instance_dataset, inst_exp_id, instance_id, size):
    instance_id = int(instance_id)
    model_experiment_obj = ExperimentFactory.getFactory().fromJson(project, dataset, experiment, db, cursor)
    validation_experiment = ExperimentFactory.getFactory().fromJson(project, instance_dataset, inst_exp_id, db, cursor)
    #get the features
    features_names, features_values = validation_experiment.getFeatures(instance_id)
    features_values = [float(value) for value in features_values]
    #get the pipeline with scaler and logistic model
    pipeline = model_experiment_obj.getModelPipeline()
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

@app.route('/getTopModelCoefficients/<project>/<dataset>/<experiment>/<size>/')
def getTopModelCoefficients(project, dataset, experiment, size):
    size = int(size)
    model_experiment_obj = ExperimentFactory.getFactory().fromJson(project, dataset, experiment, db, cursor)
    pipeline = model_experiment_obj.getModelPipeline()
    model_coefficients = pipeline.named_steps['model'].coef_[0]
    features_names = model_experiment_obj.getFeaturesNames()
    coefficients = map(lambda name, coef: (name, coef),
                          features_names, model_coefficients)
    coefficients.sort(key = lambda tup: abs(tup[1]))
    coefficients = coefficients[:-size-1:-1]
    barplot = BarPlot([x[0] for x in coefficients])
    dataset = PlotDataset([x[1] for x in coefficients], None)
    dataset.setColor(colors_tools.red)
    barplot.addDataset(dataset)
    return jsonify(barplot.toJson())
