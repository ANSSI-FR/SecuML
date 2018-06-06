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

from sqlalchemy.orm.exc import NoResultFound

from SecuML.experiments import db_tables
from SecuML.experiments.db_tables import ExperimentsAlchemy


def getExperimentRow(session, experiment_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    return query.first()


def getExperimentDetails(session, name, kind):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.name == name)
    query = query.filter(ExperimentsAlchemy.kind == kind)
    try:
        exp = query.one()
        return exp.id, exp.oldest_parent
    except NoResultFound:
        return None


def checkValidationExperiment(session, dataset_id, experiment_name):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.kind == 'Validation')
    query = query.filter(ExperimentsAlchemy.dataset_id == dataset_id)
    query = query.filter(ExperimentsAlchemy.name == experiment_name)
    try:
        exp = query.one()
        return exp
    except NoResultFound:
        return None


def getExperimentId(session, experiment_name):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.name == experiment_name)
    return query.first().id


def getProjectDataset(session, experiment_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    exp_obj = query.one()
    dataset_obj = exp_obj.dataset
    project_obj = dataset_obj.project
    dataset = dataset_obj.dataset
    project = project_obj.project
    return project, dataset


def getExperimentName(session, experiment_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    return query.first().name


def getExperimentLabelId(session, experiment_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    return query.first().annotations_id


def addExperiment(session, kind, name, dataset_id, parent):
    exp = ExperimentsAlchemy(kind=kind, name=name, dataset_id=dataset_id,
                             parent=parent)
    session.add(exp)
    session.commit()
    experiment_id = exp.id
    if parent is None:
        oldest_parent = experiment_id
    else:
        query = session.query(ExperimentsAlchemy)
        query = query.filter(ExperimentsAlchemy.id == parent)
        parent = query.one()
        oldest_parent = parent.oldest_parent
    exp.oldest_parent = oldest_parent
    session.commit()
    return experiment_id, oldest_parent


def removeExperiment(session, experiment_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    experiment = query.one()
    session.delete(experiment)
    session.commit()


def getChildren(session, experiment_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.parent == experiment_id)
    children = [r.id for r in query.all()]
    return children


def getDescriptiveStatsExp(session, experiment):
    features_filenames = experiment.features_filenames
    features_filenames = [f.split('.')[0] for f in features_filenames]
    features_filenames = '_'.join(features_filenames)
    exp_name = features_filenames + '__labelsFile_ground_truth'
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.dataset_id ==
                         experiment.dataset_id)
    query = query.filter(ExperimentsAlchemy.kind == 'DescriptiveStatistics')
    query = query.filter(ExperimentsAlchemy.name == exp_name)
    res = query.first()
    if res is not None:
        return res.id
    else:
        return None


def getExperiments(session, project, dataset, exp_kind=None):
    project_id = db_tables.checkProject(session, project)
    dataset_id = db_tables.checkDataset(session, project_id, dataset)
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.dataset_id == dataset_id)
    if exp_kind is not None:
        query = query.filter(ExperimentsAlchemy.kind == exp_kind)
    query = query.filter(ExperimentsAlchemy.parent == None)
    experiments = {}
    for exp in query.all():
        if exp.name not in list(experiments.keys()):
            experiments[exp.name] = []
        experiments[exp.name].append(exp.id)
    return experiments


def getExperimentKinds(session, dataset_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(dataset_id == dataset_id)
    query = query.distinct(ExperimentsAlchemy.kind)
    kinds = [r.kind for r in query.all()]
    return kinds


def getAllExperiments(session, project, dataset, exp_kind=None):
    project_id = db_tables.checkProject(session, project)
    dataset_id = db_tables.checkDataset(session, project_id, dataset)
    all_kinds = getExperimentKinds(session, dataset_id)
    experiments = {}
    for kind in all_kinds:
        experiments[kind] = []
        query = session.query(ExperimentsAlchemy)
        query = query.filter(ExperimentsAlchemy.dataset_id == dataset_id)
        query = query.filter(ExperimentsAlchemy.kind == kind)
        query = query.filter(ExperimentsAlchemy.parent == None)
        for exp in query.all():
            e = {'name': exp.name, 'id': exp.id}
            experiments[kind].append(e)
        if len(experiments[kind]) == 0:
            del experiments[kind]
    return experiments


def getCurrentIteration(session, experiment_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    experiment = query.one()
    return experiment.current_iter


def updateExperimentName(session, experiment_id, experiment_name):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    exp = query.one()
    exp.name = experiment_name
    session.commit()
