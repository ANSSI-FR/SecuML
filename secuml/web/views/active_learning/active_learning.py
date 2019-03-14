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
from flask import jsonify, send_file, render_template
import os.path as path
import pandas as pd

from secuml.web import app, secuml_conf, session, user_exp
from secuml.web.views.experiments import update_curr_exp

from secuml.core.tools.plots.barplot import BarPlot
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.core.tools.color import get_label_color
from secuml.core.tools.matrix import sort_data_frame

from secuml.exp.active_learning import ActiveLearningExp  # NOQA
from secuml.exp.active_learning import RcdExp  # NOQA
from secuml.exp.active_learning.celery_tasks import run_next_iter
from secuml.exp.data import annotations_db_tools
from secuml.exp.tools.db_tables import ExpAlchemy
from secuml.exp.tools.db_tables import ExpRelationshipsAlchemy


@app.route('/currentAnnotations/<exp_id>/<iteration>/')
def currentAnnotations(exp_id, iteration):
    experiment = update_curr_exp(exp_id)
    page = render_template('active_learning/current_annotations.html',
                           project=experiment.exp_conf.dataset_conf.project)
    if user_exp:
        filename = path.join(experiment.output_dir(), 'user_actions.log')
        file_exists = path.isfile(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'displayAnnotatedInstances']
        to_print = list(map(str, to_print))
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            f.write(to_print)
    return page


@app.route('/editFamilies/<exp_id>/')
def editFamilies(exp_id):
    return render_template('active_learning/edit_families.html')


@app.route('/getFamiliesBarplot/<annotations_id>/<iteration>/<label>/')
def getFamiliesBarplot(annotations_id, iteration, label):
    iteration = None if iteration == 'None' else int(iteration)
    family_counts = annotations_db_tools.get_families_counts(
                                                           session,
                                                           annotations_id,
                                                           iter_max=iteration,
                                                           label=label)
    df = pd.DataFrame({
        'families': list(family_counts.keys()),
        'counts': [family_counts[k] for k in list(family_counts.keys())]
        })
    sort_data_frame(df, 'families', ascending=True, inplace=True)
    barplot = BarPlot(list(df['families']))
    dataset = PlotDataset(list(df['counts']), 'Num. Instances')
    dataset.set_color(get_label_color(label))
    barplot.add_dataset(dataset)
    return jsonify(barplot.to_json())


@app.route('/currentAnnotationIteration/<exp_id>/')
def currentAnnotationIteration(exp_id):
    exp = update_curr_exp(exp_id)
    return str(exp.get_current_iter())


@app.route('/getIterMainModelConf/<exp_id>/<iteration>/')
def getIterMainModelConf(exp_id, iteration):
    exp = update_curr_exp(exp_id)
    query = exp.session.query(ExpAlchemy)
    query = query.join(ExpAlchemy.parents)
    query = query.filter(ExpRelationshipsAlchemy.parent_id == exp.exp_id)
    query = query.filter(ExpAlchemy.kind == 'Diadem')
    query = query.filter(ExpAlchemy.name == 'AL%i-Iter%s-main' %
                                            (exp.exp_id, iteration))
    main_model_exp_id = query.one().id
    dataset_conf = exp.exp_conf.dataset_conf
    conf_filename = path.join(secuml_conf.output_data_dir,
                              dataset_conf.project, dataset_conf.dataset,
                              str(main_model_exp_id), 'conf.json')
    return send_file(conf_filename)


@app.route('/runNextIteration/<exp_id>/<iter_num>/')
def runNextIteration(exp_id, iter_num):
    res = str(run_next_iter.s().apply_async())
    if user_exp:
        experiment = update_curr_exp(exp_id)
        filename = path.join(experiment.output_dir(),
                             'user_actions.log')
        file_exists = path.isfile(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'nextIteration', iter_num]
        to_print = list(map(str, to_print))
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            f.write(to_print)
    return res
