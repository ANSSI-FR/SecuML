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

from flask import send_file
import os.path as path

from SecuML.experiments.DimensionReduction.FeatureSelectionExperiment import FeatureSelectionExperiment
from SecuML.experiments.DimensionReduction.ProjectionExperiment import ProjectionExperiment

from SecuML.web import app
from SecuML.web.views.experiments import updateCurrentExperiment


@app.route('/getNumComponents/<experiment_id>/')
def getNumComponents(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    directory = experiment.getOutputDirectory()
    filename = 'projection_matrix.csv'
    with open(path.join(directory, filename), 'r') as f:
        header = f.readline()
        num_components = len(header.split(',')) - 1
    return str(num_components)


@app.route('/getHexBin/<experiment_id>/<x>/<y>/')
def getHexBin(experiment_id, x, y):
    experiment = updateCurrentExperiment(experiment_id)
    directory = experiment.getOutputDirectory()
    filename = 'c_' + x + '_' + y + '_hexbin.json'
    return send_file(path.join(directory, filename))


@app.route('/getProjectionMatrix/<experiment_id>/')
def getProjectionMatrix(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    directory = experiment.getOutputDirectory()
    filename = 'projection_matrix.csv'
    return send_file(path.join(directory, filename))


@app.route('/getExplVar/<experiment_id>/')
def getExplVar(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    directory = experiment.getOutputDirectory()
    filename = 'explained_variance.csv'
    return send_file(path.join(directory, filename))


@app.route('/getCumExplVar/<experiment_id>/')
def getCumExplVar(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    directory = experiment.getOutputDirectory()
    filename = 'cumuled_explained_variance.csv'
    return send_file(path.join(directory, filename))


@app.route('/getReconsErrors/<experiment_id>/')
def getReconsErrors(experiment_id):
    experiment = updateCurrentExperiment(experiment_id)
    directory = experiment.getOutputDirectory()
    filename = 'reconstruction_errors.csv'
    return send_file(path.join(directory, filename))
