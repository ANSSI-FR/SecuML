# SecuML
# Copyright (C) 2017  ANSSI
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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relationship

from SecuML.core.Data import labels_tools

Base = declarative_base()


class ProjectsAlchemy(Base):

    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project = Column(String(200))

    datasets = relationship('DatasetsAlchemy', back_populates='project',
                            uselist=True,
                            cascade='all, delete-orphan')


class DatasetsAlchemy(Base):

    __tablename__ = 'datasets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    dataset = Column(String(200))
    idents_hash = Column(String(32), nullable=False)
    ground_truth_hash = Column(String(32), nullable=True)

    project = relationship('ProjectsAlchemy', back_populates='datasets',
                           uselist=False)

    experiments = relationship('ExperimentsAlchemy', back_populates='dataset',
                               uselist=True,
                               cascade='all, delete-orphan')
    instances = relationship('InstancesAlchemy', back_populates='dataset',
                             uselist=True,
                             cascade='all, delete-orphan')


class ExperimentsAlchemy(Base):

    __tablename__ = 'experiments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'))
    kind = Column(String(200))
    name = Column(String(1000))
    parent = Column(Integer, ForeignKey('experiments.id'), nullable=True)
    oldest_parent = Column(Integer, nullable=True)
    current_iter = Column(Integer, nullable=True)

    dataset = relationship('DatasetsAlchemy', back_populates='experiments',
                           uselist=False)
    experiment_annotations = relationship('ExperimentAnnotationsAlchemy',
                                          back_populates='experiment',
                                          uselist=False,
                                          cascade='all, delete-orphan')
    children = relationship('ExperimentsAlchemy',
                            foreign_keys=[parent],
                            uselist=True,
                            cascade='all, delete-orphan')


class ExperimentAnnotationsAlchemy(Base):

    __tablename__ = 'experiment_annotations'

    annotations_id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(Integer, ForeignKey('experiments.id'),
                           nullable=False)
    annotations_type = Column(Enum('none', 'ground_truth', 'partial_annotations',
                                   name='annotations_type'),
                              nullable=False)

    experiment = relationship('ExperimentsAlchemy',
                              back_populates='experiment_annotations',
                              uselist=False)

    labels = relationship('AnnotationsAlchemy',
                          back_populates='experiment_annotations',
                          uselist=True,
                          cascade='all, delete-orphan')


class InstancesAlchemy(Base):

    __tablename__ = 'instances'

    # The order of the columns matters for the bulk insert.
    user_instance_id = Column(Integer, index=True)
    ident = Column(Text())
    timestamp = Column(DateTime())
    dataset_id = Column(Integer, ForeignKey('datasets.id'), index=True)
    row_number = Column(Integer, nullable=True)
    id = Column(Integer, primary_key=True, autoincrement=True)

    dataset = relationship('DatasetsAlchemy',
                           back_populates='instances',
                           uselist=False)
    labels = relationship('AnnotationsAlchemy',
                          back_populates='instance',
                          uselist=True,
                          cascade='all, delete-orphan')
    ground_truth = relationship('GroundTruthAlchemy',
                                back_populates='instance',
                                uselist=False,
                                cascade='all, delete-orphan')


class GroundTruthAlchemy(Base):

    __tablename__ = 'ground_truth'

    instance_id = Column(Integer, ForeignKey('instances.id'),
                         primary_key=True,
                         autoincrement=False)
    dataset_id = Column(Integer, ForeignKey('datasets.id'))

    label = Column(Enum(labels_tools.MALICIOUS, labels_tools.BENIGN,
                        name='ground_truth_enum'),
                   nullable=False)
    family = Column(String(200))

    instance = relationship('InstancesAlchemy',
                            back_populates='ground_truth',
                            uselist=False)


class AnnotationsAlchemy(Base):

    __tablename__ = 'annotations'

    instance_id = Column(Integer,
                         ForeignKey('instances.id'),
                         primary_key=True,
                         autoincrement=False)
    annotations_id = Column(Integer,
                            ForeignKey(
                                'experiment_annotations.annotations_id'),
                            primary_key=True)

    label = Column(Enum(labels_tools.MALICIOUS, labels_tools.BENIGN,
                        name='labels_enum'),
                   nullable=False)
    family = Column(String(200))

    iteration = Column(Integer)
    method = Column(String(200))

    experiment_annotations = relationship('ExperimentAnnotationsAlchemy',
                                          back_populates='labels',
                                          uselist=False)
    instance = relationship('InstancesAlchemy',
                            back_populates='labels',
                            uselist=False)


def createTables(engine):
    Base.metadata.create_all(engine)


def checkProject(session, project):
    query = session.query(ProjectsAlchemy)
    query = query.filter(ProjectsAlchemy.project == project)
    try:
        return query.one().id
    except NoResultFound:
        return None


def addProject(session, project):
    project = ProjectsAlchemy(project=project)
    session.add(project)
    session.flush()
    return project.id


def getProjects(session):
    query = session.query(ProjectsAlchemy)
    res = query.all()
    return [r.project for r in res]


def getDatasets(session, project):
    project_id = checkProject(session, project)
    if project_id is None:
        return []
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.project_id == project_id)
    res = query.all()
    return [r.dataset for r in res]


def checkDataset(session, project_id, dataset):
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.project_id == project_id)
    query = query.filter(DatasetsAlchemy.dataset == dataset)
    try:
        return query.one().id
    except NoResultFound:
        return None


def checkExperimentId(session, experiment_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    try:
        return query.one()
    except NoResultFound:
        return None


def getDatasetHashes(session, project_id, dataset_id):
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.project_id == project_id)
    query = query.filter(DatasetsAlchemy.id == dataset_id)
    res = query.one()
    return res.idents_hash, res.ground_truth_hash


def addDataset(session, project_id, dataset_name, idents_hash,
               ground_truth_hash):
    dataset = DatasetsAlchemy(project_id=project_id, dataset=dataset_name,
                              idents_hash=idents_hash,
                              ground_truth_hash=ground_truth_hash)
    session.add(dataset)
    session.flush()
    return dataset.id


def removeDataset(session, project, dataset):
    project_id = checkProject(session, project)
    if project_id is None:
        return
    dataset_id = checkDataset(session, project_id, dataset)
    if dataset_id is None:
        return
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.id == dataset_id)
    row = query.one()
    session.delete(row)
    session.flush()


def removeProject(session, project):
    project_id = checkProject(session, project)
    if project_id is None:
        return
    query = session.query(ProjectsAlchemy)
    query = query.filter(ProjectsAlchemy.id == project_id)
    row = query.one()
    session.delete(row)
    session.flush()


def getDatasetFromExperiment(session, experiment_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    exp = query.one()
    return exp.dataset_id


def hasGroundTruth(experiment):
    query = experiment.session.query(GroundTruthAlchemy)
    query = query.filter(GroundTruthAlchemy.dataset_id ==
                         experiment.dataset_id)
    return query.first() is not None


def getDatasetIds(session, dataset_id):
    query = session.query(InstancesAlchemy.id)
    query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
    query = query.order_by(InstancesAlchemy.id)
    return [r.id for r in query.all()]


def getDatasetTimestamps(session, dataset_id):
    query = session.query(InstancesAlchemy)
    query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
    query = query.order_by(InstancesAlchemy.id)
    return [r.timestamp for r in query.all()]
