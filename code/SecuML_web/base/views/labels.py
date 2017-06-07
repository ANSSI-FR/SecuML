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

from flask import jsonify

from SecuML_web.base import app, db, cursor

from SecuML.Tools import mysql_tools
from SecuML.Data import labels_tools

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
@app.route('/removeLabel/<project>/<dataset>/<experiment>/<instance_id>/')
def removeLabel(project, dataset, experiment, instance_id):
    mysql_tools.useDatabase(cursor, project, dataset)
    labels_tools.removeLabel(cursor, experiment, instance_id)
    db.commit()
    return ''

## The new label is added to the table Label
## If there is already a label for 'instance_id' in 'experiment' nothing is done.
@app.route('/addLabel/<project>/<dataset>/<experiment_label_id>/<iteration_number>/<instance_id>/<label>/<family>/<method>/<annotation>/')
def addLabel(project, dataset, experiment_label_id, iteration_number, instance_id,
        label, family, method, annotation):
    annotation = annotation == 'true'
    mysql_tools.useDatabase(cursor, project, dataset)
    labels_tools.addLabel(cursor, experiment_label_id,
            instance_id, label, family,
            iteration_number, method, annotation)
    db.commit()
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
    families = labels_tools.getDatasetFamilies(cursor, project, dataset, experiment_label_id)
    if (len(families) == 0):
        return str(False)
    if (len(families) == 1):
        if families[0] == 'other':
            return str(False)
    return str(True)

@app.route('/changeFamilyName/<project>/<dataset>/<experiment_label_id>/<label>/<family>/<new_family_name>/')
def changeFamilyName(project, dataset, experiment_label_id, label, family, new_family_name):
    mysql_tools.useDatabase(cursor, project, dataset)
    labels_tools.changeFamilyName(cursor, label, family, new_family_name, experiment_label_id)
    return ''

@app.route('/changeFamilyLabel/<project>/<dataset>/<experiment_label_id>/<label>/<family>/')
def changeFamilyLabel(project, dataset, experiment_label_id, label, family):
    mysql_tools.useDatabase(cursor, project, dataset)
    labels_tools.changeFamilyLabel(cursor, label, family, experiment_label_id)
    return ''

@app.route('/mergeFamilies/<project>/<dataset>/<experiment_label_id>/<label>/<families>/<new_family_name>/')
def mergeFamilies(project, dataset, experiment_label_id, label, families, new_family_name):
    families = families.split(',')
    mysql_tools.useDatabase(cursor, project, dataset)
    labels_tools.mergeFamilies(cursor, label, families, new_family_name, experiment_label_id)
    return ''
