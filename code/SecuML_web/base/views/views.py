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

from __future__ import division
import csv
from flask import send_file, jsonify
import importlib
import numpy as np

from SecuML_web.base import app, cursor, db

from SecuML.Experiment import ExperimentFactory
from SecuML.Plots.BarPlot import BarPlot

from SecuML.Data import idents_tools
from SecuML.Tools import mysql_tools

@app.route('/getInstance/<project>/<dataset>/<instance_id>/<ident>/')
def getInstance(project, dataset, instance_id, ident):
    module = importlib.import_module('SecuML_web.base.views.Projects.' + project)
    return module.getInstance(dataset, instance_id, ident)

@app.route('/getIdent/<project>/<dataset>/<instance_id>/')
def getIdent(project, dataset, instance_id):
    mysql_tools.useDatabase(cursor, project, dataset)
    ident = idents_tools.getIdent(cursor, instance_id)
    return ident

@app.route('/getFeatures/<project>/<dataset>/<experiment>/<validation_dataset>/<instance_id>/')
def getFeatures(project, dataset, experiment, validation_dataset, instance_id):
    instance_id = int(instance_id)
    mysql_tools.useDatabase(cursor, project, dataset)
    experiment_obj = ExperimentFactory.getFactory().fromJson(project, dataset, experiment, db, cursor)
    [feature_name, features_values] = experiment_tools.getFeatures(project, experiment_obj, validation_dataset, instance_id)
    features = map(lambda name,value: ('"' + name + '"', value), feature_name, features_values)
    features = [':'.join(sublist) for sublist in features]
    return '{' + ','.join(features) + '}'

@app.route('/getWeightedFeatures/<project>/<dataset>/<experiment>/<validation_dataset>/<instance_id>/')
def getWeightedFeatures(project, dataset, experiment, validation_dataset, instance_id):
    instance_id = int(instance_id)
    mysql_tools.useDatabase(cursor, project, dataset)
    #get the experiement
    experiment_obj = ExperimentFactory.getFactory().fromJson(project, dataset, experiment, db, cursor)
    #get the features
    [feature_name, features_values] = experiment_tools.getFeatures(project, experiment_obj, validation_dataset, instance_id)
    features_values = [float(value) for value in features_values]
    #get the pipeline with scaler and logistic model
    pipeline = experiment_tools.getModelPipeline(project, dataset, experiment)
    #scale the features
    scaled_values = pipeline.named_steps['scaler'].transform(np.reshape(features_values,(1,-1)))
    weighted_values = np.multiply(scaled_values, pipeline.named_steps['lr'].coef_)
    features = map(lambda name,value: ('"' + name + '"', str(value)), feature_name, weighted_values[0])
    features = [':'.join(sublist) for sublist in features]
    return '{' + ','.join(features) + '}'

@app.route('/getWeightedBarplot/<project>/<dataset>/<experiment>/<validation_dataset>/<instance_id>/')
def getWeightedBarplot(project, dataset, experiment, validation_dataset, instance_id):
    instance_id = int(instance_id)
    mysql_tools.useDatabase(cursor, project, dataset)
    #get the experiement
    experiment_obj = ExperimentFactory.getFactory().fromJson(project, dataset, experiment, db, cursor)
    #get the features
    [feature_name, features_values] = experiment_tools.getFeatures(project, experiment_obj, validation_dataset, instance_id)
    features_values = [float(value) for value in features_values]
    #get the pipeline with scaler and logistic model
    pipeline = experiment_tools.getModelPipeline(project, dataset, experiment)
    #scale the features
    scaled_values = pipeline.named_steps['scaler'].transform(np.reshape(features_values,(1,-1)))
    weighted_values = np.multiply(scaled_values, pipeline.named_steps['lr'].coef_)
    #create the barplot
    barplot = BarPlot(feature_name)
    barplot.addDataset(list(weighted_values[0]), 'red', instance_id)
    return barplot.getJson()
