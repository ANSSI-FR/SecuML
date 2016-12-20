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

from flask import send_file

from SecuML_web.base import app, db, cursor

from SecuML.Experiment import ExperimentFactory
from SecuML.Tools import dir_tools

@app.route('/getHexBin/<project>/<dataset>/<experiment_id>/<x>/<y>/')
def getHexBin(project, dataset, experiment_id, x, y):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    directory = dir_tools.getExperimentOutputDirectory(experiment)
    filename = directory + 'c_'+ x + '_' + y + '_hexbin.json'
    return send_file(filename)

@app.route('/getProjectionMatrix/<project>/<dataset>/<experiment_id>/')
def getProjectionMatrix(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    directory = dir_tools.getExperimentOutputDirectory(experiment)
    filename = directory + 'projection_matrix.csv'
    return send_file(filename)

@app.route('/getExplVar/<project>/<dataset>/<experiment_id>/')
def getExplVar(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    directory = dir_tools.getExperimentOutputDirectory(experiment)
    filename = directory + 'explained_variance.csv'
    return send_file(filename)

@app.route('/getCumExplVar/<project>/<dataset>/<experiment_id>/')
def getCumExplVar(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    directory = dir_tools.getExperimentOutputDirectory(experiment)
    filename = directory + 'cumuled_explained_variance.csv'
    return send_file(filename)

@app.route('/getReconsErrors/<project>/<dataset>/<experiment_id>/')
def getReconsErrors(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    directory = dir_tools.getExperimentOutputDirectory(experiment)
    filename = directory + 'reconstruction_errors.csv'
    return send_file(filename)
