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
from flask import render_template, jsonify
import json
import os.path as path
import pandas as pd

from SecuML.web import app, session, user_exp
from SecuML.web.views.experiments import updateCurrentExperiment

from SecuML.core.Tools.Plots.BarPlot import BarPlot
from SecuML.core.Tools.Plots.PlotDataset import PlotDataset
from SecuML.core.Tools import colors_tools
from SecuML.core.Tools import dir_tools
from SecuML.core.Tools import matrix_tools

from SecuML.experiments.Data import annotations_db_tools
from SecuML.experiments.ActiveLearning.ActiveLearningExperiment import ActiveLearningExperiment
from SecuML.experiments.ActiveLearning.CeleryTasks import runNextIteration as celeryRunNextIteration
from SecuML.experiments.ActiveLearning.CeleryTasks import checkAnnotationQueriesAnswered as celeryCheckAnnotationQueriesAnswered
from SecuML.experiments.ActiveLearning.IterationExp import IterationExp
from SecuML.experiments.ActiveLearning.RareCategoryDetectionExperiment import RareCategoryDetectionExperiment


@app.route('/currentAnnotations/<experiment_id>/<iteration>/')
def currentAnnotations(experiment_id, iteration):
    experiment = updateCurrentExperiment(experiment_id)
    page = render_template(
        'ActiveLearning/current_annotations.html', project=experiment.project)
    if user_exp:
        filename = path.join(experiment.getOutputDirectory(),
                             'user_actions.log')
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'displayAnnotatedInstances']
        to_print = list(map(str, to_print))
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            f.write(to_print)
    return page


@app.route('/editFamilies/<experiment_id>/')
def editFamilies(experiment_id):
    return render_template('ActiveLearning/edit_families.html')


@app.route('/getFamiliesBarplot/<experiment_id>/<iteration>/<label>/')
def getFamiliesBarplot(experiment_id, iteration, label):
    if iteration == 'None':
        iteration = None
    family_counts = annotations_db_tools.getFamiliesCounts(session,
                                                           experiment_id,
                                                           iteration_max=iteration,
                                                           label=label)
    df = pd.DataFrame({'families': list(family_counts.keys()),
                       'counts': [family_counts[k] for k in list(family_counts.keys())]})
    matrix_tools.sortDataFrame(df, 'families', ascending=True, inplace=True)
    barplot = BarPlot(list(df['families']))
    dataset = PlotDataset(list(df['counts']), 'Num. Instances')
    dataset.setColor(colors_tools.getLabelColor(label))
    barplot.addDataset(dataset)
    return jsonify(barplot.toJson())


@app.route('/currentAnnotationIteration/<experiment_id>/')
def currentAnnotationIteration(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    return str(experiment.getCurrentIteration())


@app.route('/getIterationSupervisedExperiment/<experiment_id>/<iteration>/')
def getIterationSupervisedExperiment(experiment_id, iteration):
    experiment = updateCurrentExperiment(experiment_id)
    binary_multiclass = 'multiclass'
    if 'binary' in list(experiment.conf.models_conf.keys()):
        binary_multiclass = 'binary'
    models_exp_file = path.join(experiment.getOutputDirectory(),
                                str(iteration),
                                'models_experiments.json')
    with open(models_exp_file, 'r') as f:
        models_exp = json.load(f)
    return str(models_exp[binary_multiclass])


@app.route('/runNextIteration/<experiment_id>/<iteration_number>/')
def runNextIteration(experiment_id, iteration_number):
    res = str(celeryRunNextIteration.s().apply_async())
    if user_exp:
        experiment = updateCurrentExperiment(experiment_id)
        filename = path.join(experiment.getOutputDirectory(),
                             'user_actions.log')
        file_exists = dir_tools.checkFileExists(filename)
        mode = 'a' if file_exists else 'w'
        to_print = [datetime.datetime.now(), 'nextIteration', iteration_number]
        to_print = list(map(str, to_print))
        to_print = ','.join(to_print)
        with open(filename, mode) as f:
            f.write(to_print)
    return res


@app.route('/checkAnnotationQueriesAnswered/<experiment_id>/<iteration_number>/')
def checkAnnotationQueriesAnswered(experiment_id, iteration_number):
    res = celeryCheckAnnotationQueriesAnswered.s().apply_async().get()
    return str(res)
