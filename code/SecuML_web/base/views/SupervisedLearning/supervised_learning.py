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

from flask import render_template, send_file, jsonify
import numpy as np
import pandas as pd
import random
import sys

from SecuML_web.base import app, db, cursor

from SecuML.Experiment import ExperimentFactory
from SecuML.Experiment.SupervisedLearningExperiment import SupervisedLearningExperiment
from SecuML.Plots.BarPlot import BarPlot
from SecuML.SupervisedLearning.Monitoring import AlertsMonitoring
from SecuML.Tools import dir_tools, mysql_tools

def getDir(project, dataset, experiment_id, iteration):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    directory = dir_tools.getExperimentOutputDirectory(experiment)
    if iteration != 'None':
        directory += str(iteration) + '/'
    return directory

@app.route('/alerts/<project>/<dataset>/<experiment>/<iteration>/')
def displayAlertsMenu(project, dataset, experiment, iteration):
    return render_template('SupervisedLearning/alerts_menu.html')

@app.route('/alerts/<project>/<dataset>/<experiment>/<iteration>/<analysis_type>/')
def displayAlerts(project, dataset, experiment, iteration, analysis_type):
    return render_template('SupervisedLearning/alerts.html', project = project)

@app.route('/familiesPerformance/<project>/<dataset>/<experiment>/<iteration>/<train_test>/')
def displayFamiliesPerformance(project, dataset, experiment, iteration, train_test):
    return render_template('SupervisedLearning/families_performance.html', project = project)

@app.route('/errors/<project>/<dataset>/<experiment>/<iteration>/<train_test>/<experiment_label_id>/')
def displayErrors(project, dataset, experiment, iteration, train_test, experiment_label_id):
    return render_template('SupervisedLearning/errors.html', project = project)

@app.route('/getValidationDataset/<project>/<dataset>/<experiment_id>/')
def getValidationDataset(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    test_conf = experiment.supervised_learning_conf.test_conf
    if test_conf.method == 'test_dataset':
        return test_conf.test_dataset
    else:
        return dataset

@app.route('/getAlertsClusteringExperimentId/<project>/<dataset>/<experiment_id>/')
def getAlertsClusteringExperimentId(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    test_conf = experiment.supervised_learning_conf.test_conf
    if test_conf.method == 'random_split':
        test_dataset = dataset
        test_exp_id = experiment_id
    elif test_conf.method == 'test_dataset':
        test_dataset = test_conf.test_exp.dataset
        test_exp_id = test_conf.test_exp.experiment_id
    mysql_tools.useDatabase(cursor, project, test_dataset)
    clustering_experiment_id = AlertsMonitoring.AlertsMonitoring.getAlertsClusteringExperimentId(
            cursor, test_exp_id)
    return str(clustering_experiment_id)

@app.route('/getAlerts/<project>/<dataset>/<experiment_id>/<iteration>/<analysis_type>/')
def getAlerts(project, dataset, experiment_id, iteration, analysis_type):
    filename  = getDir(project, dataset, experiment_id, iteration)
    filename += 'alerts.csv'
    with open(filename, 'r') as f:
        data = pd.read_csv(f, header = 0, index_col = 0)
        experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
                db, cursor)
        num_max_alerts = experiment.supervised_learning_conf.test_conf.alerts_conf.num_max_alerts
        alerts = list(data.index.values)
        if num_max_alerts < len(alerts):
            if analysis_type == 'topN':
                alerts = alerts[:num_max_alerts]
            elif analysis_type == 'random':
                alerts = random.sample(alerts, num_max_alerts)
    return jsonify({'instances': alerts})

@app.route('/getPredictionsDensityPNG/<project>/<dataset>/<experiment>/<iteration>/<train_test>/')
def getPredictionsDensityPNG(project, dataset, experiment, iteration, train_test):
    filename  = getDir(project, dataset, experiment, iteration) + train_test + '/'
    filename += 'families/labels_distributions.png'
    return send_file(filename, mimetype='image/png')

@app.route('/getPredictionsBarplot/<project>/<dataset>/<experiment>/<iteration>/<train_test>/')
def getPredictionsBarplot(project, dataset, experiment, iteration, train_test):
    filename  = getDir(project, dataset, experiment, iteration) + train_test + '/'
    filename += 'predictions_barplot.json'
    return send_file(filename)

@app.route('/getPredictionsBarplotLabels/<project>/<dataset>/<experiment>/<iteration>/<train_test>/')
def getPredictionsBarplotLabels(project, dataset, experiment, iteration, train_test):
    filename  = getDir(project, dataset, experiment, iteration) + train_test + '/'
    filename += 'predictions_barplot_labels.json'
    return send_file(filename)

@app.route('/getPerformanceIndicators/<project>/<dataset>/<experiment>/<iteration>/<train_test>/<subkind>/')
def getPerformanceIndicators(project, dataset, experiment, iteration, train_test, subkind):
    filename  = getDir(project, dataset, experiment, iteration) + train_test + '/'
    if train_test == 'labels':
        if subkind == 'all':
            filename += 'global_'
    filename += 'perf_indicators.json'
    return send_file(filename)

@app.route('/getRoc/<project>/<dataset>/<experiment>/<iteration>/<train_test>/')
def getRoc(project, dataset, experiment, iteration, train_test):
    filename  = getDir(project, dataset, experiment, iteration) + train_test + '/'
    filename += 'ROC.png'
    return send_file(filename, mimetype='image/png')

@app.route('/getFamiliesRoc/<project>/<dataset>/<experiment>/<iteration>/<train_test>/')
def getFamiliesRoc(project, dataset, experiment, iteration, train_test):
    filename  = getDir(project, dataset, experiment, iteration) + train_test + '/families/'
    filename += 'fp_fn_families_thresholds.png'
    return send_file(filename, mimetype='image/png')

@app.route('/getConfusionMatrix/<project>/<dataset>/<experiment>/<iteration>/<train_test>/<subkind>/')
def getConfusionMatrix(project, dataset, experiment, iteration, train_test, subkind):
    filename  = getDir(project, dataset, experiment, iteration) + train_test + '/'
    if train_test == 'labels':
        if subkind == 'all':
            filename += 'global_'
    filename += 'confusion_matrix.json'
    return send_file(filename)

@app.route('/getErrors/<project>/<dataset>/<experiment>/<iteration>/<train_test>/')
def getErrors(project, dataset, experiment, iteration, train_test):
    filename  = getDir(project, dataset, experiment, iteration) + train_test + '/'
    filename += 'errors.json'
    return send_file(filename)

@app.route('/getFamiliesPerformance/<project>/<dataset>/<experiment>/<iteration>/<train_test>/<label>/<threshold>/')
def getFamiliesPerformance(project, dataset, experiment, iteration, train_test, label, threshold):
    filename  = getDir(project, dataset, experiment, iteration) + train_test + '/families/'
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
        barplot.addDataset(perf, 'blue', tp_fp)
    return jsonify(barplot.barplot);

@app.route('/getModelCoefficients/<project>/<dataset>/<experiment>/<iteration>/')
def getModelCoefficients(project, dataset, experiment, iteration):
    if iteration != 'None':
        # Active Learning
        return False
    else:
        # Supervised Learning
        pipeline = experiment_tools.getModelPipeline(project, dataset, experiment)
        return list(pipeline.named_steps['lr'].coef_[0])

@app.route('/getModelIntercept/<project>/<dataset>/<experiment>/<iteration>/')
def getModelIntercept(project, dataset, experiment, iteration):
    if iteration != 'None':
        # Active Learning
        return False
    else:
        # Supervised Learning
        pipeline = experiment_tools.getModelPipeline(project, dataset, experiment)
        return pipeline.named_steps['lr'].intercept_[0]

@app.route('/getCoefBarplot/<project>/<dataset>/<experiment>/')
def getCoefBarplot(project, dataset, experiment):
    mysql_tools.useDatabase(cursor, project, dataset)
    #get the experiement
    experiment_obj = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    #get the features
    [features_name, features_values] = experiment_tools.getFeatures(project, experiment_obj)
    #get the pipeline with scaler and logistic model
    pipeline = experiment_tools.getModelPipeline(project, dataset, experiment)
    #scale the features
    coefficients = pipeline.named_steps['lr'].coef_[0]
    best_coef_index = np.argsort(np.absolute(coefficients))[-20:]
    best_features_name = [features_name[index] for index in best_coef_index]
    best_coef = [coefficients[index] for index in best_coef_index]
    #create the barplot
    barplot = BarPlot(best_features_name)
    barplot.addDataset(list(best_coef), 'red', 0)
    return barplot.getJson()
