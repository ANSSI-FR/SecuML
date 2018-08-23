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

import datetime
from flask import jsonify
import os.path as path

from SecuML.web import app, user_exp, session
from SecuML.web.views.experiments import updateCurrentExperiment

from SecuML.core.Data import labels_tools
from SecuML.core.Tools import dir_tools

from SecuML.experiments.Data import annotations_db_tools


@app.route('/getAnnotation/<experiment_id>/<instance_id>/')
def getAnnotation(experiment_id, instance_id):
    annotation = annotations_db_tools.getAnnotation(session,
                                                    experiment_id,
                                                    instance_id)
    if annotation is None:
        annotation = {}
    else:
        annotation = {'label': annotation[0], 'family': annotation[1]}
    return jsonify(annotation)

# If there is already an annotation for 'instance_id' in 'experiment',
# then the annotation is removed
# Otherwise, nothing is done


@app.route('/removeAnnotation/<experiment_id>/<inst_experiment_id>/<iteration_number>/<instance_id>/')
def removeAnnotation(experiment_id, inst_experiment_id, iteration_number, instance_id):
    annotations_db_tools.removeAnnotation(
        session, inst_experiment_id, instance_id)
    session.commit()
    if user_exp:
        experiment = updateCurrentExperiment(experiment_id)
        filename = path.join(experiment.getOutputDirectory(),
                             'user_actions.log')
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'removeAnnotation', instance_id]
        to_print = list(map(str, to_print))
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            f.write(to_print)
    return ''

# The new annotation is added.
# If there is already an annotation for 'instance_id' in 'experiment' nothing is done.
@app.route('/addAnnotation/<experiment_id>/<inst_experiment_id>/<iteration_number>/<instance_id>/<label>/<family>/<method>/')
def addAnnotation(experiment_id, inst_experiment_id, iteration_number, instance_id, label, family, method):
    annotations_db_tools.addAnnotation(session, inst_experiment_id,
                                       instance_id, label, family,
                                       iteration_number, method)
    session.commit()
    if user_exp:
        experiment = updateCurrentExperiment(experiment_id)
        filename = path.join(experiment.getOutputDirectory(),
                             'user_actions.log')
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'addAnnotation',
                    iteration_number, instance_id, label, family, method]
        to_print = list(map(str, to_print))
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            f.write(to_print)
    return ''


@app.route('/getAnnotatedInstances/<experiment_id>/')
def getAnnotatedInstances(experiment_id):
    res = {}
    for label in [labels_tools.MALICIOUS, labels_tools.BENIGN]:
        res[label] = annotations_db_tools.getLabelIds(session, experiment_id,
                                                      label)
    return jsonify(res)


@app.route('/getLabelsFamilies/<experiment_id>/<iteration_max>/')
def getLabelsFamilies(experiment_id, iteration_max):
    if iteration_max == 'None':
        iteration_max = None
    else:
        iteration_max = int(iteration_max)
    labels_families = annotations_db_tools.getLabelsFamilies(session,
                                                             experiment_id, iteration_max=iteration_max)
    return jsonify(labels_families)


@app.route('/getFamiliesInstances/<experiment_id>/<label>/<iteration_max>/')
def getFamiliesInstances(experiment_id, label, iteration_max):
    if iteration_max == 'None':
        iteration_max = None
    else:
        iteration_max = int(iteration_max)
    families = annotations_db_tools.getLabelsFamilies(session, experiment_id,
                                                      iteration_max=iteration_max)[label]
    families_instances = {}
    for f in families:
        families_instances[f] = annotations_db_tools.getLabelFamilyIds(session, experiment_id,
                                                                       label, family=f,
                                                                       iteration_max=iteration_max)
    return jsonify(families_instances)


@app.route('/datasetHasFamilies/<experiment_id>/')
def datasetHasFamilies(experiment_id):
    has_families = annotations_db_tools.datasetHasFamilies(
        session, experiment_id)
    return str(has_families)


@app.route('/changeFamilyName/<experiment_id>/<label>/<family>/<new_family_name>/')
def changeFamilyName(experiment_id, label, family, new_family_name):
    annotations_db_tools.changeFamilyName(session, experiment_id, label, family,
                                          new_family_name)
    session.commit()
    if user_exp:
        experiment = updateCurrentExperiment(experiment_id)
        filename = path.join(experiment.getOutputDirectory(),
                             'user_actions.log')
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'changeFamilyName',
                    family, new_family_name]
        to_print = list(map(str, to_print))
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            f.write(to_print)
    return ''


@app.route('/changeFamilyLabel/<experiment_id>/<label>/<family>/')
def changeFamilyLabel(experiment_id, label, family):
    annotations_db_tools.changeFamilyLabel(session, experiment_id, label,
                                           family)
    session.commit()
    if user_exp:
        experiment = updateCurrentExperiment(experiment_id)
        filename = path.join(experiment.getOutputDirectory(),
                             'user_actions.log')
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'changeFamilyLabel',
                    family, label]
        to_print = list(map(str, to_print))
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            f.write(to_print)
    return ''


@app.route('/mergeFamilies/<experiment_id>/<label>/<families>/<new_family_name>/')
def mergeFamilies(experiment_id, label, families, new_family_name):
    families = families.split(',')
    annotations_db_tools.mergeFamilies(session, experiment_id, label, families,
                                       new_family_name)
    session.commit()
    if user_exp:
        experiment = updateCurrentExperiment(experiment_id)
        filename = path.join(experiment.getOutputDirectory(),
                             'user_actions.log')
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'mergeFamilies', new_family_name]
        to_print += list(map(str, families))
        to_print = list(map(str, to_print))
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            f.write(to_print)
    return ''
