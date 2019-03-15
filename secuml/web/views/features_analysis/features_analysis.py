# SecuML
# Copyright (C) 2016-2019  ANSSI
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

from decimal import Decimal
from flask import jsonify, send_file
import os.path as path
import pandas as pd

from secuml.web import app, session
from secuml.web.views.experiments import update_curr_exp

from secuml.core.tools.matrix import sort_data_frame
from secuml.exp.tools.db_tables import FeaturesAlchemy
from secuml.exp.features_analysis import FeaturesAnalysisExperiment   # NOQA


@app.route('/getFeaturesInfo/<exp_id>/')
def getFeaturesInfo(exp_id):
    exp = update_curr_exp(exp_id)
    features_set_id = exp.exp_conf.features_conf.set_id
    query = session.query(FeaturesAlchemy)
    query = query.filter(FeaturesAlchemy.set_id == features_set_id)
    return jsonify({res.id: {'type': res.type,
                             'user_id': res.user_id,
                             'name': res.name,
                             'description': res.description
                             } for res in query.all()})


@app.route('/getSortingCriteria/<exp_id>/')
def getSortingCriteria(exp_id):
    exp = update_curr_exp(exp_id)
    scoring_filename = path.join(exp.output_dir(), 'scores.csv')
    scores = pd.read_csv(scoring_filename, header=0, index_col=0)
    criteria = scores.columns.values.tolist()
    criteria = list(set([c.split('_pvalues')[0] for c in criteria]))
    criteria.extend(['alphabet', 'null_variance'])
    criteria.sort()
    return jsonify({'criteria': criteria})


def get_feature_user_ids(session, features):
    user_ids = [None for _ in range(len(features))]
    for i, feature_id in enumerate(features):
        query = session.query(FeaturesAlchemy)
        query = query.filter(FeaturesAlchemy.id == feature_id)
        user_ids[i] = query.one().user_id
    return user_ids


@app.route('/getSortedFeatures/<exp_id>/<criterion>/')
def getSortedFeatures(exp_id, criterion):
    exp = update_curr_exp(exp_id)
    scoring_filename = path.join(exp.output_dir(), 'scores.csv')
    scores = pd.read_csv(scoring_filename, header=0, index_col=0)
    pvalues = None
    if criterion == 'alphabet':
        features = scores.index.values.tolist()
        features.sort()
        values = None
        user_ids = get_feature_user_ids(session, features)
        return jsonify({'features': features, 'values': None, 'pvalues': None,
                        'user_ids': user_ids})
    if criterion == 'null_variance':
        selection = scores.loc[:, 'variance'] == 0
        scores = scores.loc[selection, :]
        criterion = 'variance'
    else:
        sort_data_frame(scores, criterion, False, True)
    features = scores.index.values.tolist()
    values = scores[criterion].tolist()
    values = ['%.2f' % v for v in values]
    pvalues_col = '_'.join([criterion, 'pvalues'])
    if pvalues_col in scores.columns:
        pvalues = scores[pvalues_col].tolist()
        pvalues = ['%.2E' % Decimal(v) for v in pvalues]
    user_ids = get_feature_user_ids(session, features)
    return jsonify({'features': features, 'values': values, 'pvalues': pvalues,
                    'user_ids': user_ids})


@app.route('/getFeatureScores/<exp_id>/<feature>/')
def getFeatureScores(exp_id, feature):
    exp = update_curr_exp(exp_id)
    return send_file(path.join(exp.output_dir(), feature, 'scores.json'))


@app.route('/getStatsPlot/<exp_id>/<plot_type>/<feature>/')
def getStatsPlot(exp_id, plot_type, feature):
    exp = update_curr_exp(exp_id)
    if plot_type.find('histogram') >= 0:
        filename = plot_type + '.json'
    else:
        filename = plot_type + '.png'
    return send_file(path.join(exp.output_dir(), feature, filename))


@app.route('/getCriterionDensity/<exp_id>/<criterion>/')
def getCriterionDensity(exp_id, criterion):
    exp = update_curr_exp(exp_id)
    return send_file(path.join(exp.output_dir(), '%s_density.png' % criterion))
