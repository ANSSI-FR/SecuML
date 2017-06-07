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

from flask import jsonify, render_template, send_file
import pandas as pd

from SecuML_web.base import app, db, cursor
from SecuML_web.base.views.nocache import nocache

from SecuML.Experiment.ActiveLearningExperiment import ActiveLearningExperiment
from SecuML.Experiment import ExperimentFactory
from SecuML.Tools import dir_tools

@app.route('/getAnnotationsTypes/<project>/<dataset>/<experiment_id>/<iteration>/')
@nocache
def getAnnotationsTypes(project, dataset, experiment_id, iteration):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    filename  = dir_tools.getExperimentOutputDirectory(experiment) + str(iteration) + '/'
    filename += 'annotations_types.json'
    return send_file(filename)

@app.route('/getFamiliesInstancesToAnnotate/<project>/<dataset>/<experiment_id>/<iteration>/<predicted_label>/')
def getFamiliesInstancesToAnnotate(project, dataset, experiment_id, iteration, predicted_label):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    filename  = dir_tools.getExperimentOutputDirectory(experiment) + str(iteration) + '/'
    filename += 'toannotate_' + predicted_label + '.json'
    return send_file(filename)

@app.route('/getInstancesToAnnotate/<project>/<dataset>/<experiment_id>/<iteration>/<predicted_label>/')
def getInstancesToAnnotate(project, dataset, experiment_id, iteration, predicted_label):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    filename  = dir_tools.getExperimentOutputDirectory(experiment) + str(iteration) + '/'
    filename += 'toannotate_' + predicted_label + '.csv'
    df = pd.read_csv(filename)
    queries = list(df.instance_id)
    return jsonify({'instances': queries})

@app.route('/individualAnnotations/<project>/<dataset>/<experiment_id>/<iteration>/<predicted_label>/')
def individualAnnotations(project, dataset, experiment_id, iteration, predicted_label):
    return render_template('ActiveLearning/individual_annotations.html', project = project)

@app.route('/ilabAnnotations/<project>/<dataset>/<experiment_id>/<iteration>/')
def ilabAnnotations(project, dataset, experiment_id, iteration):
    return render_template('ActiveLearning/ilab_annotations.html', project = project)

@app.route('/rareCategoryDetectionAnnotations/<project>/<dataset>/<experiment_id>/<iteration>/')
def rareCategoryDetectionAnnotations(project, dataset, experiment_id, iteration):
    return render_template('ActiveLearning/rare_category_detection_annotations.html', project = project)
