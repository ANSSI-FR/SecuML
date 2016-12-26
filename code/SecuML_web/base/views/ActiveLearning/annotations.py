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

from flask import render_template, jsonify

from SecuML_web.base import app, db, cursor

from SecuML.Experiment.ActiveLearningExperiment import ActiveLearningExperiment
from SecuML.Experiment import experiment_db_tools
from SecuML.Experiment import ExperimentFactory
from SecuML.Tools import dir_tools, mysql_tools, set_tools

@app.route('/activeLearningAnnotationsMenu/<project>/<dataset>/<experiment_id>/<iteration>/')
def activeLearningAnnotationsMenu(project, dataset, experiment_id, iteration):
    return render_template('ActiveLearning/annotations.html')

@app.route('/clusteringAnalysis/<project>/<dataset>/<experiment_id>/<iteration>/<predicted_label>/')
def clusteringAnalysis(project, dataset, experiment_id, iteration, predicted_label):
    db.commit()
    mysql_tools.useDatabase(cursor, project, dataset)
    clustering = experiment_db_tools.clusteringPredictedLabelsAnalysis(cursor,
            experiment_id, iteration, predicted_label)
    return str(clustering)

@app.route('/getInstancesToAnnotate/<project>/<dataset>/<experiment_id>/<iteration>/<predicted_label>/')
def getInstancesToAnnotate(project, dataset, experiment_id, iteration, predicted_label):
    experiment = ExperimentFactory.getFactory().fromJson(project, dataset, experiment_id,
            db, cursor)
    filename  = dir_tools.getExperimentOutputDirectory(experiment) + str(iteration) + '/'
    filename += 'toannotate_' + predicted_label + '.csv'
    instances = set_tools.loadSet(filename, True)
    res = {}
    res['instances'] = list(instances)
    return jsonify(res)

@app.route('/individualAnnotations/<project>/<dataset>/<experiment_id>/<iteration>/<predicted_label>/')
def individualAnnotations(project, dataset, experiment_id, iteration, predicted_label):
    return render_template('ActiveLearning/individual_annotations.html', project = project)
