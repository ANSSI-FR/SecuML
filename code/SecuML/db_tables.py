## SecuML
## Copyright (C) 2017  ANSSI
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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Boolean
from sqlalchemy import delete
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import ForeignKeyConstraint

Base = declarative_base()

class ProjectsAlchemy(Base):

    __tablename__ = 'Projects'

    id          = Column(Integer, primary_key = True, autoincrement = True)
    project     = Column(String(200))
    datasets    = relationship('DatasetsAlchemy', back_populates = 'project',
                               cascade = 'all, delete-orphan')

class DatasetsAlchemy(Base):

    __tablename__ = 'Datasets'

    id          = Column(Integer, primary_key = True, autoincrement = True)
    project_id  = Column(Integer, ForeignKey('Projects.id'))
    dataset     = Column(String(200))
    project     = relationship('ProjectsAlchemy', back_populates = 'datasets')
    experiments = relationship('ExperimentsAlchemy', back_populates = 'dataset',
                               cascade = 'all, delete-orphan')
    instances   = relationship('InstancesAlchemy', back_populates = 'dataset',
                               cascade = 'all, delete-orphan')

class ExperimentsAlchemy(Base):

    __tablename__ = 'Experiments'

    id            = Column(Integer, primary_key = True, autoincrement = True)
    dataset_id    = Column(Integer, ForeignKey('Datasets.id'), primary_key=True)
    kind          = Column(String(200))
    name          = Column(String(1000))
    parent        = Column(Integer, ForeignKey('Experiments.id'), nullable = True)
    oldest_parent = Column(Integer, nullable = True)
    current_iter  = Column(Integer, nullable = True)
    annotations   = Column(Boolean, nullable = True)
    labels        = relationship('LabelsAlchemy', back_populates = 'experiment',
                                 cascade = 'all, delete-orphan')
    children      = relationship('ExperimentsAlchemy',
                                 foreign_keys = [parent],
                                 cascade = 'all, delete-orphan')
    dataset       = relationship('DatasetsAlchemy', back_populates = 'experiments')

class InstancesAlchemy(Base):

    __tablename__ = 'Instances'

    # The order of the columns matters for the bulk insert.
    instance_id = Column(Integer, primary_key = True, autoincrement = False)
    ident       = Column(String(200))
    dataset_id  = Column(Integer, ForeignKey('Datasets.id'), primary_key = True)
    row_number  = Column(Integer, nullable = True)
    dataset     = relationship('DatasetsAlchemy', back_populates = 'instances')

class LabelsAlchemy(Base):

    __tablename__ = 'Labels'

    instance_id   = Column(Integer, primary_key = True, autoincrement = False)
    label         = Column(String(200))
    family        = Column(String(200))

    experiment_id = Column(Integer, ForeignKey('Experiments.id'), primary_key = True)
    dataset_id    = Column(Integer, nullable = False)
    iteration     = Column(Integer)
    method        = Column(String(200))
    annotation    = Column(Boolean)

    ForeignKeyConstraint(columns = [dataset_id, instance_id],
                         refcolumns = [InstancesAlchemy.dataset_id, InstancesAlchemy.instance_id])

    experiment    = relationship('ExperimentsAlchemy', back_populates = 'labels')
    instance      = relationship('InstancesAlchemy',
                                 foreign_keys = [InstancesAlchemy.instance_id, InstancesAlchemy.dataset_id],
                                 primaryjoin = 'and_(LabelsAlchemy.instance_id == InstancesAlchemy.instance_id, LabelsAlchemy.dataset_id == InstancesAlchemy.dataset_id)',
                                 uselist = False,
                                 backref = backref('labels',
                                                    primaryjoin = 'and_(LabelsAlchemy.instance_id == InstancesAlchemy.instance_id, LabelsAlchemy.dataset_id == InstancesAlchemy.dataset_id)',
                                                    uselist = True))

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
    project = ProjectsAlchemy(project = project)
    session.add(project)
    session.commit()
    return project.id

def checkDataset(session, project_id, dataset):
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.project_id == project_id)
    query = query.filter(DatasetsAlchemy.dataset == dataset)
    try:
        return query.one().id
    except NoResultFound:
        return None

def addDataset(session, project_id, dataset_name):
    dataset = DatasetsAlchemy(project_id = project_id, dataset = dataset_name)
    session.add(dataset)
    session.commit()
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
    session.commit()

def removeProject(session, project):
    project_id = checkProject(session, project)
    if project_id is None:
        return
    query = session.query(ProjectsAlchemy)
    query = query.filter(ProjectsAlchemy.id == project_id)
    row = query.one()
    session.delete(row)
    session.commit()

def getDatasetFromExperiment(session, experiment_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    exp = query.one()
    return exp.dataset_id

def hasTrueLabels(experiment):
    query = experiment.session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.dataset_id == experiment.dataset_id)
    query = query.filter(ExperimentsAlchemy.kind == 'TrueLabels')
    try:
        true_labels_exp = query.one()
        return true_labels_exp.id
    except NoResultFound:
        return None
