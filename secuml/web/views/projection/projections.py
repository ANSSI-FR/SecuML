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

from flask import send_file
import os.path as path

from secuml.exp.projection import ProjectionExperiment  # NOQA

from secuml.web import app
from secuml.web.views.experiments import update_curr_exp


@app.route('/getNumComponents/<exp_id>/')
def getNumComponents(exp_id):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = 'projection_matrix.csv'
    with open(path.join(directory, filename), 'r') as f:
        header = f.readline()
        num_components = len(header.split(',')) - 1
    return str(num_components)


@app.route('/getHexBin/<exp_id>/<x>/<y>/')
def getHexBin(exp_id, x, y):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = '_'.join(['c', x, y, 'hexbin.json'])
    return send_file(path.join(directory, filename))


@app.route('/getProjectionMatrix/<exp_id>/')
def getProjectionMatrix(exp_id):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = 'projection_matrix.csv'
    return send_file(path.join(directory, filename))


@app.route('/getExplVar/<exp_id>/')
def getExplVar(exp_id):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = 'explained_variance.csv'
    return send_file(path.join(directory, filename))


@app.route('/getCumExplVar/<exp_id>/')
def getCumExplVar(exp_id):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = 'cumuled_explained_variance.csv'
    return send_file(path.join(directory, filename))


@app.route('/getReconsErrors/<exp_id>/')
def getReconsErrors(exp_id):
    experiment = update_curr_exp(exp_id)
    directory = experiment.output_dir()
    filename = 'reconstruction_errors.csv'
    return send_file(path.join(directory, filename))
