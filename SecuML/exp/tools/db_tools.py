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

from sqlalchemy import desc

from SecuML.exp import db_tables
from SecuML.exp.db_tables import ActiveLearningExpAlchemy
from SecuML.exp.db_tables import FeaturesAnalysisExpAlchemy
from SecuML.exp.db_tables import ExpAlchemy


def getExperimentRow(session, experiment_id):
    query = session.query(ExpAlchemy)
    query = query.filter(ExpAlchemy.id == experiment_id)
    return query.first()


def getProjectDataset(session, experiment_id):
    query = session.query(ExpAlchemy)
    query = query.filter(ExpAlchemy.id == experiment_id)
    exp_obj = query.one()
    dataset_obj = exp_obj.dataset
    project_obj = dataset_obj.project
    return project_obj.project, dataset_obj.dataset


def getFeaturesAnalysisExp(session, exp):
    dataset_features_id = exp.exp_conf.features_conf.dataset_features_id
    query = session.query(FeaturesAnalysisExpAlchemy)
    query = query.filter(FeaturesAnalysisExpAlchemy.dataset_features_id ==
                         dataset_features_id)
    query = query.filter(FeaturesAnalysisExpAlchemy.annotations_filename ==
                         'ground_truth.csv')
    query = query.order_by(desc(FeaturesAnalysisExpAlchemy.id))
    res = query.first()
    if res is not None:
        return res.id
    else:
        query = session.query(FeaturesAnalysisExpAlchemy)
        query = query.filter(FeaturesAnalysisExpAlchemy.dataset_features_id ==
                             dataset_features_id)
        query = query.order_by(desc(FeaturesAnalysisExpAlchemy.id))
        res = query.first()
        if res is not None:
            return res.id
        else:
            return None


def getAllExperiments(session, project, dataset, exp_kind=None):
    project_id = db_tables.checkProject(session, project)
    dataset_id = db_tables.checkDataset(session, project_id, dataset)
    query = session.query(ExpAlchemy)
    query = query.filter(ExpAlchemy.dataset_id == dataset_id)
    query = query.filter(ExpAlchemy.parent == None)
    experiments = {}
    for exp in query.all():
        kind = exp.kind
        if kind not in experiments:
            experiments[kind] = []
        experiments[kind].append({'name': exp.name, 'id': exp.id})
    return experiments


def getCurrentIteration(session, experiment_id):
    query = session.query(ActiveLearningExpAlchemy)
    query = query.filter(ActiveLearningExpAlchemy.id == experiment_id)
    return query.one().current_iter
