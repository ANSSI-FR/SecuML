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

from SecuML_web.base import app, session

from flask import jsonify, render_template

from SecuML import db_tables
from SecuML.Experiment import experiment_db_tools
from SecuML.Experiment import ExperimentFactory

from SecuML.Experiment.FeatureSelectionExperiment import FeatureSelectionExperiment

def updateCurrentExperiment(experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(experiment_id, session)
    return experiment

@app.route('/SecuML/<project>/<dataset>/<exp_type>/menu/')
def expMenu(project, dataset, exp_type):
    return render_template('experiments_menu.html')

@app.route('/SecuML/<experiment_id>/')
def getExperiment(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template(experiment.webTemplate(), project = experiment.project)

@app.route('/hasTrueLabels/<experiment_id>/')
def hasTrueLabels(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    true_labels_exp_id =  db_tables.hasTrueLabels(experiment)
    return str(true_labels_exp_id is not None)

@app.route('/getTrueLabelsExperiment/<experiment_id>/')
def getTrueLabelsExperiment(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    true_labels_exp_id =  db_tables.hasTrueLabels(experiment)
    return str(true_labels_exp_id)

@app.route('/getConf/<experiment_id>/')
def getConf(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    conf = experiment.toJson()
    conf['has_true_labels'] = db_tables.hasTrueLabels(experiment)
    return jsonify(conf)

@app.route('/getExperimentsNames/<project>/<dataset>/<exp_kind>/')
def getExperimentsNames(project, dataset, exp_kind):
    experiments = experiment_db_tools.getExperiments(session, project, dataset, exp_kind)
    return jsonify(experiments)

@app.route('/getExperimentLabelId/<experiment_id>/')
def getExperimentLabelId(experiment_id):
    experiment_label_id = experiment_db_tools.getExperimentLabelId(session, experiment_id)
    return str(experiment_label_id)

@app.route('/getExperimentName/<experiment_id>/')
def getExperimentName(experiment_id):
    return experiment_db_tools.getExperimentName(session, experiment_id)




@app.route('/getDescriptiveStatsExp/<experiment_id>/')
def getDescriptiveStatsExp(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    return str(experiment_db_tools.getDescriptiveStatsExp(experiment.session, experiment))


@app.route('/SecuML/<experiment_id>/<feature>/')
def getDescriptiveStatsExperiment(experiment_id, feature):
    experiment = updateCurrentExperiment(experiment_id)
    return render_template(experiment.webTemplate(), feature = {'feature': feature})
