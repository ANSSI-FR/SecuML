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

import datetime
from flask import jsonify

from SecuML_web.base import app, db, cursor, user_exp

from SecuML.Data import labels_tools
from SecuML.Experiment import ExperimentFactory
from SecuML.Tools import dir_tools, mysql_tools

@app.route('/getLabel/<project>/<dataset>/<experiment_label_id>/<instance_id>/')
def getLabel(project, dataset, experiment_label_id, instance_id):
    mysql_tools.useDatabase(cursor, project, dataset)
    label = labels_tools.getLabel(cursor, instance_id,
            experiment_label_id = experiment_label_id)
    if label is None:
        label = {}
    else:
        label = {'label': label[0], 'family': label[1]}
    return jsonify(label)

## If there is a label for 'instance_id' in 'experiment',
## then the label is removed
## Otherwise, nothing is done
@app.route('/removeLabel/<project>/<dataset>/<experiment_id>/<inst_dataset>/<inst_experiment_label_id>/<iteration_number>/<instance_id>/')
def removeLabel(project, dataset, experiment_id, inst_dataset, inst_experiment_label_id, iteration_number, instance_id):
    mysql_tools.useDatabase(cursor, project, inst_dataset)
    labels_tools.removeLabel(cursor, inst_experiment_label_id, instance_id)
    db.commit()
    if user_exp:
        experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
                                                             db, cursor)
        filename  = dir_tools.getExperimentOutputDirectory(experiment)
        filename += 'user_actions.log'
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'removeLabel', project, dataset, instance_id]
        to_print = map(str, to_print)
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            print >>f, to_print
    return ''

## The new label is added to the table Label
## If there is already a label for 'instance_id' in 'experiment' nothing is done.
@app.route('/addLabel/<project>/<dataset>/<experiment_id>/<inst_dataset>/<inst_experiment_label_id>/<iteration_number>/<instance_id>/<label>/<family>/<method>/<annotation>/')
def addLabel(project, dataset, experiment_id, inst_dataset, inst_experiment_label_id, iteration_number, instance_id,
        label, family, method, annotation):
    annotation = annotation == 'true'
    mysql_tools.useDatabase(cursor, project, inst_dataset)
    labels_tools.addLabel(cursor, inst_experiment_label_id,
            instance_id, label, family,
            iteration_number, method, annotation)
    db.commit()
    if user_exp:
        experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
                                                             db, cursor)
        filename  = dir_tools.getExperimentOutputDirectory(experiment)
        filename += 'user_actions.log'
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'addLabel', project, dataset, iteration_number, instance_id, label, family, method, annotation]
        to_print = map(str, to_print)
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            print >>f, to_print
    return ''

@app.route('/getLabeledInstances/<project>/<dataset>/<experiment_label_id>/')
def getLabeledInstances(project, dataset, experiment_label_id):
    mysql_tools.useDatabase(cursor, project, dataset)
    res = {}
    res['malicious'] = labels_tools.getLabelIds(cursor, 'malicious', experiment_label_id,
            annotation = True)
    res['benign'] = labels_tools.getLabelIds(cursor, 'benign', experiment_label_id,
            annotation = True)
    return jsonify(res)

@app.route('/getLabelsFamilies/<project>/<dataset>/<experiment_label_id>/<iteration_max>/')
def getLabelsFamilies(project, dataset, experiment_label_id, iteration_max):
    if iteration_max == 'None':
        iteration_max = None
    else:
        iteration_max = int(iteration_max)
    mysql_tools.useDatabase(cursor, project, dataset)
    db.commit()
    labels_families = labels_tools.getLabelsFamilies(cursor,
            experiment_label_id, iteration_max = iteration_max)
    return jsonify(labels_families)

@app.route('/getFamiliesInstances/<project>/<dataset>/<experiment_label_id>/<label>/<iteration_max>/')
def getFamiliesInstances(project, dataset, experiment_label_id, label, iteration_max):
    if iteration_max == 'None':
        iteration_max = None
    else:
        iteration_max = int(iteration_max)
    mysql_tools.useDatabase(cursor, project, dataset)
    db.commit()
    families = labels_tools.getLabelsFamilies(cursor, experiment_label_id, iteration_max = iteration_max)[label]
    families_instances = {}
    for f in families:
        families_instances[f] = labels_tools.getLabelFamilyIds(cursor, experiment_label_id, label, family = f,
                                                               iteration_max = iteration_max)
    return jsonify(families_instances)

@app.route('/datasetHasFamilies/<project>/<dataset>/<experiment_label_id>/')
def datasetHasFamilies(project, dataset, experiment_label_id):
    mysql_tools.useDatabase(cursor, project, dataset)
    has_families = labels_tools.datasetHasFamilies(cursor, project, dataset, experiment_label_id)
    return str(has_families)

@app.route('/changeFamilyName/<project>/<dataset>/<experiment_id>/<experiment_label_id>/<label>/<family>/<new_family_name>/')
def changeFamilyName(project, dataset, experiment_id, experiment_label_id, label, family, new_family_name):
    mysql_tools.useDatabase(cursor, project, dataset)
    labels_tools.changeFamilyName(cursor, label, family, new_family_name, experiment_label_id)
    if user_exp:
        experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
                                                             db, cursor)
        filename  = dir_tools.getExperimentOutputDirectory(experiment)
        filename += 'user_actions.log'
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'changeFamilyName',family, new_family_name]
        to_print = map(str, to_print)
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            print >>f, to_print
    return ''

@app.route('/changeFamilyLabel/<project>/<dataset>/<experiment_id>/<experiment_label_id>/<label>/<family>/')
def changeFamilyLabel(project, dataset, experiment_id, experiment_label_id, label, family):
    mysql_tools.useDatabase(cursor, project, dataset)
    labels_tools.changeFamilyLabel(cursor, label, family, experiment_label_id)
    if user_exp:
        experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
                                                             db, cursor)
        filename  = dir_tools.getExperimentOutputDirectory(experiment)
        filename += 'user_actions.log'
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'changeFamilyLabel',family, label]
        to_print = map(str, to_print)
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            print >>f, to_print
    return ''

@app.route('/mergeFamilies/<project>/<dataset>/<experiment_id>/<experiment_label_id>/<label>/<families>/<new_family_name>/')
def mergeFamilies(project, dataset, experiment_id, experiment_label_id, label, families, new_family_name):
    families = families.split(',')
    mysql_tools.useDatabase(cursor, project, dataset)
    labels_tools.mergeFamilies(cursor, label, families, new_family_name, experiment_label_id)
    if user_exp:
        experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
                                                             db, cursor)
        filename  = dir_tools.getExperimentOutputDirectory(experiment)
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
