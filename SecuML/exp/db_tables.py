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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relationship

from SecuML.core.data import labels_tools

Base = declarative_base()


class ProjectsAlchemy(Base):

    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project = Column(String(200), index=True)

    datasets = relationship('DatasetsAlchemy', back_populates='project',
                            uselist=True, cascade='all, delete-orphan')


class DatasetsAlchemy(Base):

    __tablename__ = 'datasets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    dataset = Column(String(200), index=True)

    project = relationship('ProjectsAlchemy', back_populates='datasets',
                           uselist=False)
    hashes = relationship('DatasetsHashesAlchemy', back_populates='dataset',
                          uselist=False, cascade='all, delete-orphan')
    instances = relationship('InstancesAlchemy', back_populates='dataset',
                             uselist=True, cascade='all, delete-orphan')
    features = relationship('DatasetFeaturesAlchemy', back_populates='dataset',
                            uselist=True, cascade='all, delete-orphan')
    experiments = relationship('ExpAlchemy', back_populates='dataset',
                               uselist=True, cascade='all, delete-orphan')


class DatasetsHashesAlchemy(Base):

    __tablename__ = 'datasets_hashes'

    id = Column(Integer, ForeignKey('datasets.id'), primary_key=True)
    idents_hash = Column(String(32), nullable=False)
    ground_truth_hash = Column(String(32), nullable=True)

    dataset = relationship('DatasetsAlchemy', back_populates='hashes',
                           uselist=False)


class ExpAlchemy(Base):

    __tablename__ = 'experiments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_features_id = Column(Integer, ForeignKey('dataset_features.id'))
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    annotations_id = Column(Integer, ForeignKey('exp_annotations.id'))
    kind = Column(Enum('FeaturesAnalysis', 'ActiveLearning',
                       'RareCategoryDetection', 'Classification', 'Validation',
                       'Clustering', 'Projection', 'FeatureSelection',
                        name='exp_kind'),
                  nullable=False)
    name = Column(String(1000))
    parent = Column(Integer, ForeignKey('experiments.id'), nullable=True)


    dataset = relationship('DatasetsAlchemy', back_populates='experiments',
                           uselist=False)
    dataset_features = relationship('DatasetFeaturesAlchemy',
                                    back_populates='experiments',
                                    uselist=False)
    exp_annotations = relationship('ExpAnnotationsAlchemy',
                                   back_populates='exp', uselist=False,
                                   single_parent=True,
                                   cascade='all, delete-orphan')
    children = relationship('ExpAlchemy',
                            foreign_keys=[parent],
                            uselist=True,
                            cascade='all, delete-orphan')
    active_learning_exp = relationship('ActiveLearningExpAlchemy',
                                       back_populates='exp',
                                       uselist=False,
                                       cascade='all, delete-orphan')
    features_analysis_exp = relationship('FeaturesAnalysisExpAlchemy',
                                         back_populates='exp',
                                         uselist=False,
                                         cascade='all, delete-orphan')
    alerts_clustering_exp = relationship('AlertsClusteringExpAlchemy',
                                         back_populates='diadem_exp',
                                         uselist=False,
                                         cascade='all, delete-orphan')


class ActiveLearningExpAlchemy(Base):

    __tablename__ = 'active_learning_exp'

    id = Column(Integer, ForeignKey('experiments.id'), primary_key=True)
    current_iter = Column(Integer, nullable=False)
    finished = Column(Boolean, nullable=False)

    exp = relationship('ExpAlchemy', back_populates='active_learning_exp',
                       uselist=False)


class AlertsClusteringExpAlchemy(Base):

    __tablename__ = 'alerts_clustering_exp'

    diadem_id = Column(Integer, ForeignKey('experiments.id'), primary_key=True)
    clustering_id = Column(Integer, nullable=False)

    diadem_exp = relationship('ExpAlchemy',
                              back_populates='alerts_clustering_exp',
                              uselist=False)


class FeaturesAnalysisExpAlchemy(Base):

    __tablename__ = 'features_analysis_exp'

    id = Column(Integer, ForeignKey('experiments.id'), primary_key=True)
    dataset_features_id = Column(Integer, ForeignKey('dataset_features.id'),
                                 nullable=False)
    annotations_filename = Column(String(1000), nullable=False, index=True)

    exp = relationship('ExpAlchemy', back_populates='features_analysis_exp',
                       uselist=False)
    dataset = relationship('DatasetFeaturesAlchemy',
                           back_populates='features_analysis_exp',
                           uselist=False)


class ExpAnnotationsAlchemy(Base):

    __tablename__ = 'exp_annotations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum('none', 'ground_truth', 'partial',
                       name='annotations_type'),
                  nullable=False)

    exp = relationship('ExpAlchemy', back_populates='exp_annotations',
                       uselist=True)
    annotations = relationship('AnnotationsAlchemy',
                               back_populates='exp_annotations',
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
    annotations = relationship('AnnotationsAlchemy',
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

    instance_id = Column(Integer, ForeignKey('instances.id'), primary_key=True,
                         autoincrement=False)
    annotations_id = Column(Integer, ForeignKey('exp_annotations.id'),
                            primary_key=True)
    label = Column(Enum(labels_tools.MALICIOUS, labels_tools.BENIGN,
                        name='labels_enum'),
                   nullable=False)
    family = Column(String(200))
    iteration = Column(Integer)
    method = Column(String(200))

    exp_annotations = relationship('ExpAnnotationsAlchemy',
                                   back_populates='annotations',
                                   uselist=False)
    instance = relationship('InstancesAlchemy', back_populates='annotations',
                            uselist=False)


class DatasetFeaturesAlchemy(Base):

    __tablename__ = 'dataset_features'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    name = Column(String(256), nullable=False, index=True)
    type = Column(Enum('file', 'dir', name='file_dir_enum'), nullable=False)

    dataset = relationship('DatasetsAlchemy', back_populates='features',
                           uselist=False)
    experiments = relationship('ExpAlchemy', back_populates='dataset_features',
                               uselist=True,
                               cascade='all, delete-orphan')
    files = relationship('FeaturesFilesAlchemy',
                         back_populates='dataset_features', uselist=True,
                         cascade='all, delete-orphan')
    features = relationship('FeaturesAlchemy',
                            back_populates='features_dataset', uselist=True,
                            cascade='all, delete-orphan')
    features_analysis_exp = relationship('FeaturesAnalysisExpAlchemy',
                                         back_populates='dataset',
                                         uselist=True,
                                         cascade='all, delete-orphan')


class FeaturesFilesAlchemy(Base):

    __tablename__ = 'features_files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_features_id = Column(Integer, ForeignKey('dataset_features.id'),
                                 nullable=False)
    filename = Column(String(256), nullable=False)
    hash = Column(String(32), nullable=False)

    dataset_features = relationship('DatasetFeaturesAlchemy',
                                    back_populates='files', uselist=False)
    features = relationship('FeaturesAlchemy', back_populates='features_file',
                            uselist=True)

class FeaturesAlchemy(Base):

    __tablename__ = 'features'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Text, nullable=False)
    file_id = Column(Integer, ForeignKey('features_files.id'), nullable=False)
    dataset_features_id = Column(Integer, ForeignKey('dataset_features.id'),
                                 nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

    features_file = relationship('FeaturesFilesAlchemy',
                                 back_populates='features', uselist=False)
    features_dataset = relationship('DatasetFeaturesAlchemy',
                                    back_populates='features', uselist=False)


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
    query = session.query(ExpAlchemy)
    query = query.filter(ExpAlchemy.id == experiment_id)
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


def add_dataset(session, project_id, dataset_name):
    dataset = DatasetsAlchemy(project_id=project_id, dataset=dataset_name)
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
    query = session.query(ExpAlchemy)
    query = query.filter(ExpAlchemy.id == experiment_id)
    return query.one().dataset_id


def hasGroundTruth(session, dataset_id):
    query = session.query(GroundTruthAlchemy)
    query = query.filter(GroundTruthAlchemy.dataset_id == dataset_id)
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
