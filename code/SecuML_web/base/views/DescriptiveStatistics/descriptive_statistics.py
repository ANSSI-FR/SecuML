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

from SecuML.Experiment.DescriptiveStatisticsExperiment import DescriptiveStatisticsExperiment
from SecuML.Experiment import ExperimentFactory
from SecuML.Tools import dir_tools

@app.route('/getFeaturesTypes/<project>/<dataset>/<experiment_id>/')
def getFeaturesTypes(project, dataset, experiment_id):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    filename  = dir_tools.getExperimentOutputDirectory(experiment)
    filename += 'features_types.json'
    return send_file(filename)

@app.route('/getStatsPlot/<project>/<dataset>/<experiment_id>/<plot_type>/<feature>/')
def getStatsPlot(project, dataset, experiment_id, plot_type, feature):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    filename  = dir_tools.getExperimentOutputDirectory(experiment) + feature + '/'
    if plot_type.find('histogram') >= 0:
        filename += plot_type + '.json'
    else:
        filename += plot_type + '.png'
    return send_file(filename)
