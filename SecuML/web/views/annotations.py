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

import datetime
from flask import jsonify
import os.path as path

from SecuML.web import app, user_exp, session
from SecuML.web.views.experiments import updateCurrentExperiment

from SecuML.exp.conf.AnnotationsConf import AnnotationsTypes
from SecuML.exp.data import annotations_db_tools


@app.route('/getAnnotation/<annotations_type>/<annotations_id>/<dataset_id>/'
           '<instance_id>/')
def getAnnotation(annotations_type, annotations_id, dataset_id, instance_id):
    annotations_type = AnnotationsTypes[annotations_type]
    annotation = annotations_db_tools.getAnnotation(session,
                                                    annotations_type,
                                                    annotations_id,
                                                    dataset_id,
                                                    instance_id)
    if annotation is None:
        return jsonify({})
    else:
        return jsonify({'label': annotation[0], 'family': annotation[1]})


# If there is already an annotation for 'instance_id' in 'experiment',
# then the annotation is removed
# Otherwise, nothing is done
@app.route('/removeAnnotation/<exp_id>/<inst_exp_id><instance_id>/')
def removeAnnotation(exp_id, inst_exp_id, instance_id):
    annotations_db_tools.removeAnnotation(session, inst_exp_id, instance_id)
    session.commit()
    if user_exp:
        exp = updateCurrentExperiment(exp_id)
        filename = path.join(exp.output_dir(), 'user_actions.log')
        file_exists = path.isfile(filename)
        mode = 'a' if file_exists else 'w'
        to_print = ','.join(map(str, [datetime.datetime.now(),
                                      'removeAnnotation', instance_id]))
        with open(filename, mode) as f:
            f.write(to_print)
    return ''

@app.route('/updateAnnotation/<exp_id>/<inst_annotations_id>/<iter_num>/'
           '<instance_id>/<label>/<family>/<method>/')
def updateAnnotation(exp_id, inst_annotations_id, iter_num, instance_id, label,
                     family, method):
    iter_num = None if iter_num == 'None' else int(iter_num)
    annotations_db_tools.updateAnnotation(session, inst_annotations_id,
                                          instance_id, label, family,
                                          iter_num, method)
    session.commit()
    if user_exp:
        exp = updateCurrentExperiment(exp_id)
        filename = path.join(exp.output_dir(), 'user_actions.log')
        file_exists = path.isfile(filename)
        mode = 'a' if file_exists else 'w'
        to_print = ','.join(map(str, [datetime.datetime.now(), 'addAnnotation',
                                      iter_num, instance_id, label, family,
                                      method]))
        with open(filename, mode) as f:
            f.write(to_print)
    return ''


@app.route('/getLabelsFamilies/<annotations_type>/<annotations_id>/'
           '<dataset_id>/<iter_max>/')
def getLabelsFamilies(annotations_type, annotations_id, dataset_id, iter_max):
    iter_max = None if iter_max == 'None' else int(iter_max)
    annotations_type = AnnotationsTypes[annotations_type]
    return jsonify(annotations_db_tools.get_labels_families(session,
                                                            annotations_type,
                                                            annotations_id,
                                                            dataset_id,
                                                            iter_max=iter_max))


@app.route('/getFamiliesInstances/<annotations_type>/<annotations_id>/'
           '<dataset_id>/<label>/<iter_max>/')
def getFamiliesInstances(annotations_type, annotations_id, dataset_id, label,
                         iter_max):
    annotations_type = AnnotationsTypes[annotations_type]
    iter_max = None if iter_max == 'None' else int(iter_max)
    families = annotations_db_tools.get_labels_families(session,
                                                        annotations_type,
                                                        annotations_id,
                                                        dataset_id,
                                                        iter_max=iter_max)
    instances = {}
    for f in families[label]:
        instances[f] = annotations_db_tools.get_label_family_ids(session,
                                                              annotations_type,
                                                              annotations_id,
                                                              dataset_id,
                                                              label,
                                                              family=f,
                                                              iter_max=iter_max)
    return jsonify(instances)


@app.route('/datasetHasFamilies/<annotations_id>/')
def datasetHasFamilies(annotations_id):
    return str(annotations_db_tools.datasetHasFamilies(session, annotations_id))


@app.route('/changeFamilyName/<exp_id>/<annotations_id>/<label>/<family>/'
           '<new_family>/')
def changeFamilyName(exp_id, annotations_id, label, family, new_family):
    annotations_db_tools.changeFamilyName(session, annotations_id, label,
                                          family, new_family)
    session.commit()
    if user_exp:
        exp = updateCurrentExperiment(exp_id)
        filename = path.join(exp.output_dir(), 'user_actions.log')
        file_exists = path.isfile(filename)
        mode = 'a' if file_exists else 'w'
        to_print = ','.join(map(str, [datetime.datetime.now(),
                                      'changeFamilyName', family, new_family]))
        with open(filename, mode) as f:
            f.write(to_print)
    return ''


@app.route('/changeFamilyLabel/<exp_id>/<annotations_id>/<label>/<family>/')
def changeFamilyLabel(exp_id, annotations_id, label, family):
    annotations_db_tools.changeFamilyLabel(session, annotations_id, label,
                                           family)
    session.commit()
    if user_exp:
        exp = updateCurrentExperiment(exp_id)
        filename = path.join(exp.output_dir(), 'user_actions.log')
        file_exists = path.isfile(filename)
        mode = 'a' if file_exists else 'w'
        to_print = ','.join(map(str, [datetime.datetime.now(),
                                      'changeFamilyLabel', family, label]))
        with open(filename, mode) as f:
            f.write(to_print)
    return ''


@app.route('/mergeFamilies/<exp_id>/<annotations_id>/<label>/<families>/'
           '<new_family>/')
def mergeFamilies(exp_id, annotations_id, label, families, new_family):
    families = families.split(',')
    annotations_db_tools.mergeFamilies(session, annotations_id, label, families,
                                       new_family)
    session.commit()
    if user_exp:
        exp = updateCurrentExperiment(exp_id)
        filename = path.join(exp.output_dir(), 'user_actions.log')
        file_exists = path.isfile(filename)
        mode = 'a' if file_exists else 'w'
        to_print = ','.join(map(str, [datetime.datetime.now(), 'mergeFamilies',
                                      new_family] + families))
        with open(filename, mode) as f:
            f.write(to_print)
    return ''
