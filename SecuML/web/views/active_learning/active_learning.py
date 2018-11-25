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
from flask import render_template, jsonify
import json
import os.path as path
import pandas as pd

from SecuML.web import app, session, user_exp
from SecuML.web.views.experiments import updateCurrentExperiment

from SecuML.core.tools.plots.BarPlot import BarPlot
from SecuML.core.tools.plots.PlotDataset import PlotDataset
from SecuML.core.tools import colors_tools
from SecuML.core.tools import matrix_tools

from SecuML.exp.data import annotations_db_tools
from SecuML.exp.active_learning.ActiveLearningExperiment \
        import ActiveLearningExperiment
from SecuML.exp.active_learning.CeleryTasks \
        import runNextIteration as celeryRunNextIteration


@app.route('/currentAnnotations/<exp_id>/<iteration>/')
def currentAnnotations(exp_id, iteration):
    experiment = updateCurrentExperiment(exp_id)
    page = render_template('active_learning/current_annotations.html',
                           project=experiment.exp_conf.dataset_conf.project)
    if user_exp:
        filename = path.join(experiment.output_dir(),
                             'user_actions.log')
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
    family_counts = annotations_db_tools.getFamiliesCounts(session,
                                                           annotations_id,
                                                           iter_max=iteration,
                                                           label=label)
    df = pd.DataFrame({
        'families': list(family_counts.keys()),
        'counts': [family_counts[k] for k in list(family_counts.keys())]
        })
    matrix_tools.sort_data_frame(df, 'families', ascending=True, inplace=True)
    barplot = BarPlot(list(df['families']))
    dataset = PlotDataset(list(df['counts']), 'Num. Instances')
    dataset.set_color(colors_tools.get_label_color(label))
    barplot.add_dataset(dataset)
    return jsonify(barplot.to_json())


@app.route('/currentAnnotationIteration/<exp_id>/')
def currentAnnotationIteration(exp_id):
    exp = updateCurrentExperiment(exp_id)
    return str(exp.getCurrentIteration())


@app.route('/getIterationSupervisedExperiment/<exp_id>/<iteration>/')
def getIterationSupervisedExperiment(exp_id, iteration):
    experiment = updateCurrentExperiment(exp_id)
    binary_multiclass = 'multiclass'
    if 'binary' in experiment.exp_conf.core_conf.models_conf.__dict__:
        binary_multiclass = 'binary'
    models_exp_file = path.join(experiment.output_dir(),
                                str(iteration),
                                'models_experiments.json')
    with open(models_exp_file, 'r') as f:
        models_exp = json.load(f)
    return str(models_exp[binary_multiclass])


@app.route('/runNextIteration/<exp_id>/<iteration_number>/')
def runNextIteration(exp_id, iteration_number):
    res = str(celeryRunNextIteration.s().apply_async())
    if user_exp:
        experiment = updateCurrentExperiment(exp_id)
        filename = path.join(experiment.output_dir(),
                             'user_actions.log')
        file_exists = path.isfile(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'nextIteration', iteration_number]
        to_print = list(map(str, to_print))
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            f.write(to_print)
    return res
