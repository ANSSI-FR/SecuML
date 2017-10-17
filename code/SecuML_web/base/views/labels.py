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

import datetime
from flask import jsonify

from SecuML_web.base import app, user_exp, session
from SecuML_web.base.views.experiments import updateCurrentExperiment

from SecuML.Data import labels_tools
from SecuML.Tools import dir_tools

@app.route('/getLabel/<experiment_label_id>/<instance_id>/')
def getLabel(experiment_label_id, instance_id):
    label = labels_tools.getLabel(session, instance_id,
                                  experiment_label_id)
    if label is None:
        label = {}
    else:
        label = {'label': label[0], 'family': label[1]}
    return jsonify(label)

## If there is a label for 'instance_id' in 'experiment',
## then the label is removed
## Otherwise, nothing is done
@app.route('/removeLabel/<experiment_id>/<inst_experiment_label_id>/<iteration_number>/<instance_id>/')
def removeLabel(experiment_id, inst_experiment_label_id, iteration_number, instance_id):
    labels_tools.removeLabel(session, inst_experiment_label_id, instance_id)
    if user_exp:
        experiment = updateCurrentExperiment(experiment_id)
        filename  = experiment.getOutputDirectory()
        filename += 'user_actions.log'
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'removeLabel', instance_id]
        to_print = map(str, to_print)
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            print >>f, to_print
    return ''

## The new label is added to the table Label
## If there is already a label for 'instance_id' in 'experiment' nothing is done.
@app.route('/addLabel/<experiment_id>/<inst_experiment_label_id>/<iteration_number>/<instance_id>/<label>/<family>/<method>/<annotation>/')
def addLabel(experiment_id, inst_experiment_label_id, iteration_number, instance_id,
             label, family, method, annotation):
    annotation = annotation == 'true'
    labels_tools.addLabel(session, inst_experiment_label_id,
            instance_id, label, family,
            iteration_number, method, annotation)
    if user_exp:
        experiment = updateCurrentExperiment(experiment_id)
        filename  = experiment.getOutputDirectory()
        filename += 'user_actions.log'
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'addLabel', iteration_number, instance_id, label, family, method, annotation]
        to_print = map(str, to_print)
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            print >>f, to_print
    return ''

@app.route('/getLabeledInstances/<experiment_id>/')
def getLabeledInstances(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    experiment_label_id = experiment.labels_id
    res = {}
    res['malicious'] = labels_tools.getLabelIds(session, 'malicious', experiment_label_id,
            annotation = True)
    res['benign'] = labels_tools.getLabelIds(session, 'benign', experiment_label_id,
            annotation = True)
    return jsonify(res)

@app.route('/getLabelsFamilies/<experiment_id>/<iteration_max>/')
def getLabelsFamilies(experiment_id, iteration_max):
    experiment = updateCurrentExperiment(experiment_id)
    if iteration_max == 'None':
        iteration_max = None
    else:
        iteration_max = int(iteration_max)
    labels_families = labels_tools.getLabelsFamilies(session,
            experiment.labels_id, iteration_max = iteration_max)
    return jsonify(labels_families)

@app.route('/getFamiliesInstances/<experiment_id>/<label>/<iteration_max>/')
def getFamiliesInstances(experiment_id, label, iteration_max):
    experiment = updateCurrentExperiment(experiment_id)
    if iteration_max == 'None':
        iteration_max = None
    else:
        iteration_max = int(iteration_max)
    families = labels_tools.getLabelsFamilies(session, experiment.labels_id,
                                              iteration_max = iteration_max)[label]
    families_instances = {}
    for f in families:
        families_instances[f] = labels_tools.getLabelFamilyIds(session, experiment.labels_id,
                                                               label, family = f,
                                                               iteration_max = iteration_max)
    return jsonify(families_instances)

@app.route('/datasetHasFamilies/<experiment_id>/')
def datasetHasFamilies(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    experiment_label_id = experiment.labels_id
    has_families = labels_tools.datasetHasFamilies(session, experiment_label_id)
    return str(has_families)

@app.route('/changeFamilyName/<experiment_id>/<label>/<family>/<new_family_name>/')
def changeFamilyName(experiment_id, label, family, new_family_name):
    experiment = updateCurrentExperiment(experiment_id)
    experiment_label_id = experiment.labels_id
    labels_tools.changeFamilyName(session, label, family, new_family_name, experiment_label_id)
    if user_exp:
        filename  = experiment.getOutputDirectory()
        filename += 'user_actions.log'
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'changeFamilyName',family, new_family_name]
        to_print = map(str, to_print)
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            print >>f, to_print
    return ''

@app.route('/changeFamilyLabel/<experiment_id>/<label>/<family>/')
def changeFamilyLabel(experiment_id, label, family):
    experiment = updateCurrentExperiment(experiment_id)
    experiment_label_id = experiment.labels_id
    labels_tools.changeFamilyLabel(session, label, family, experiment_label_id)
    if user_exp:
        filename  = experiment.getOutputDirectory()
        filename += 'user_actions.log'
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'changeFamilyLabel',family, label]
        to_print = map(str, to_print)
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            print >>f, to_print
    return ''

@app.route('/mergeFamilies/<experiment_id>/<label>/<families>/<new_family_name>/')
def mergeFamilies(experiment_id, label, families, new_family_name):
    experiment = updateCurrentExperiment(experiment_id)
    experiment_label_id = experiment.labels_id
    families = families.split(',')
    labels_tools.mergeFamilies(session, label, families, new_family_name, experiment_label_id)
    if user_exp:
        filename  = experiment.getOutputDirectory()
        filename += 'user_actions.log'
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'mergeFamilies', new_family_name]
        to_print += map(str, families)
        to_print = map(str, to_print)
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            print >>f, to_print
    return ''
