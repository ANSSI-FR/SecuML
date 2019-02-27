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
from sqlalchemy.orm import relationship

from secuml.core.data.labels_tools import BENIGN, MALICIOUS


Base = declarative_base()


class DatasetsAlchemy(Base):

    __tablename__ = 'datasets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project = Column(String(200), index=True)
    dataset = Column(String(200), index=True)
    idents_hash = Column(String(32), nullable=False)
    ground_truth_hash = Column(String(32), nullable=True)

    instances = relationship('InstancesAlchemy', back_populates='dataset',
                             uselist=True, cascade='all, delete-orphan')
    features = relationship('FeaturesSetsAlchemy', back_populates='dataset',
                            uselist=True, cascade='all, delete-orphan')


class ExpAlchemy(Base):

    __tablename__ = 'experiments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    features_set_id = Column(Integer, ForeignKey('features_set.id',
                                                 ondelete='CASCADE'))
    annotations_id = Column(Integer, ForeignKey('exp_annotations.id',
                                                ondelete='CASCADE'))
    kind = Column(Enum('FeaturesAnalysis', 'ActiveLearning', 'Rcd', 'Diadem',
                       'Train', 'Test', 'Clustering', 'Projection',
                       name='exp_kind'),
                  nullable=False)
    name = Column(String(1000))

    features_set = relationship('FeaturesSetsAlchemy',
                                back_populates='experiments',
                                uselist=False)
    exp_annotations = relationship('ExpAnnotationsAlchemy',
                                   back_populates='exp', uselist=False,
                                   single_parent=True,
                                   cascade='all, delete-orphan')

    diadem_exp = relationship('DiademExpAlchemy',
                              back_populates='exp',
                              uselist=False,
                              cascade='all, delete-orphan')
    features_analysis_exp = relationship('FeaturesAnalysisExpAlchemy',
                                         back_populates='exp',
                                         uselist=False,
                                         cascade='all, delete-orphan')
    active_learning_exp = relationship('ActiveLearningExpAlchemy',
                                       back_populates='exp',
                                       uselist=False,
                                       cascade='all, delete-orphan')


class ExpRelationshipsAlchemy(Base):

    __tablename__ = 'exp_relationships'

    child_id = Column(Integer, ForeignKey('experiments.id'), primary_key=True)
    parent_id = Column(Integer, ForeignKey('experiments.id'), primary_key=True)

    child = relationship('ExpAlchemy', backref='parents', uselist=False,
                         foreign_keys=[child_id])
    parent = relationship('ExpAlchemy', backref='children', uselist=False,
                          foreign_keys=[parent_id])


class DiademExpAlchemy(Base):

    __tablename__ = 'diadem_exp'

    exp_id = Column(Integer, ForeignKey('experiments.id', ondelete='CASCADE'),
                    primary_key=True)
    fold_id = Column(Integer, nullable=True)
    type = Column(Enum('train', 'cv', 'test', 'validation', 'alerts',
                       name='diadem_exp_type'),
                  nullable=False)
    alerts = Column(Boolean, nullable=True)
    perf_monitoring = Column(Boolean, nullable=True)
    model_interpretation = Column(Boolean, nullable=True)
    predictions_interpretation = Column(Boolean, nullable=True)
    multiclass = Column(Boolean, nullable=True)
    proba = Column(Boolean, nullable=True)
    with_scoring = Column(Boolean, nullable=True)

    exp = relationship('ExpAlchemy', back_populates='diadem_exp',
                       uselist=False)


class ActiveLearningExpAlchemy(Base):

    __tablename__ = 'active_learning_exp'

    id = Column(Integer, ForeignKey('experiments.id', ondelete='CASCADE'),
                primary_key=True)
    current_iter = Column(Integer, nullable=False)
    finished = Column(Boolean, nullable=False)

    exp = relationship('ExpAlchemy', back_populates='active_learning_exp',
                       uselist=False)
    ilab_exp = relationship('IlabExpAlchemy', back_populates='al_exp',
                            uselist=True, cascade='all, delete-orphan')
    rcd_exp = relationship('RcdClusteringExpAlchemy', back_populates='al_exp',
                           uselist=True, cascade='all, delete-orphan')


class IlabExpAlchemy(Base):

    __tablename__ = 'ilab_exp'

    id = Column(Integer,
                ForeignKey('active_learning_exp.id', ondelete='CASCADE'),
                primary_key=True)
    iter = Column(Integer, primary_key=True)
    # null: the queries are not available yet.
    # -1:   the queries are available, but there is no clustering analysis.
    # >= 0: the queries are available, the id of the clustering experiment.
    uncertain = Column(Integer, nullable=True)
    malicious = Column(Integer, nullable=True)
    benign = Column(Integer, nullable=True)

    al_exp = relationship('ActiveLearningExpAlchemy',
                          back_populates='ilab_exp', uselist=False)


class RcdClusteringExpAlchemy(Base):

    __tablename__ = 'rcd_exp'

    id = Column(Integer,
                ForeignKey('active_learning_exp.id', ondelete='CASCADE'),
                primary_key=True)
    iter = Column(Integer, primary_key=True)
    # -1:   there is no clustering analysis.
    # >= 0: the id of the clustering experiment.
    clustering_exp = Column(Integer, nullable=True)

    al_exp = relationship('ActiveLearningExpAlchemy', back_populates='rcd_exp',
                          uselist=False)


class FeaturesAnalysisExpAlchemy(Base):

    __tablename__ = 'features_analysis_exp'

    id = Column(Integer, ForeignKey('experiments.id', ondelete='CASCADE'),
                primary_key=True)
    features_set_id = Column(Integer, ForeignKey('features_set.id'),
                             nullable=False)
    annotations_filename = Column(String(1000), nullable=False, index=True)

    exp = relationship('ExpAlchemy', back_populates='features_analysis_exp',
                       uselist=False)
    dataset = relationship('FeaturesSetsAlchemy',
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
    dataset_id = Column(Integer, ForeignKey('datasets.id', ondelete='CASCADE'),
                        index=True)
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

    instance_id = Column(Integer,
                         ForeignKey('instances.id', ondelete='CASCADE'),
                         primary_key=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id', ondelete='CASCADE'))

    label = Column(Enum(MALICIOUS, BENIGN, name='ground_truth_enum'),
                   nullable=False)
    family = Column(String(200))

    instance = relationship('InstancesAlchemy',
                            back_populates='ground_truth',
                            uselist=False)


class AnnotationsAlchemy(Base):

    __tablename__ = 'annotations'

    instance_id = Column(Integer,
                         ForeignKey('instances.id', ondelete='CASCADE'),
                         primary_key=True)
    annotations_id = Column(Integer,
                            ForeignKey('exp_annotations.id',
                                       ondelete='CASCADE'),
                            primary_key=True)
    label = Column(Enum(MALICIOUS, BENIGN, name='labels_enum'),
                   nullable=False)
    family = Column(String(200))
    iteration = Column(Integer)
    method = Column(String(200))

    exp_annotations = relationship('ExpAnnotationsAlchemy',
                                   back_populates='annotations',
                                   uselist=False)
    instance = relationship('InstancesAlchemy', back_populates='annotations',
                            uselist=False)


class FeaturesSetsAlchemy(Base):

    __tablename__ = 'features_set'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id', ondelete='CASCADE'),
                        nullable=False)
    name = Column(String(256), nullable=False, index=True)
    type = Column(Enum('file', 'dir', name='file_dir_enum'), nullable=False)

    dataset = relationship('DatasetsAlchemy', back_populates='features',
                           uselist=False)
    experiments = relationship('ExpAlchemy', back_populates='features_set',
                               uselist=True,
                               cascade='all, delete-orphan')
    files = relationship('FeaturesFilesAlchemy',
                         back_populates='features_set', uselist=True,
                         cascade='all, delete-orphan')
    features = relationship('FeaturesAlchemy',
                            back_populates='features_set', uselist=True,
                            cascade='all, delete-orphan')
    features_analysis_exp = relationship('FeaturesAnalysisExpAlchemy',
                                         back_populates='dataset',
                                         uselist=True,
                                         cascade='all, delete-orphan')


class FeaturesFilesAlchemy(Base):

    __tablename__ = 'features_files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    features_set_id = Column(Integer, ForeignKey('features_set.id',
                                                 ondelete='CASCADE'),
                             nullable=False)
    filename = Column(String(256), nullable=False)
    hash = Column(String(32), nullable=False)

    features_set = relationship('FeaturesSetsAlchemy',
                                back_populates='files', uselist=False)
    features = relationship('FeaturesAlchemy', back_populates='features_file',
                            uselist=True)


class FeaturesAlchemy(Base):

    __tablename__ = 'features'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Text, nullable=False)
    file_id = Column(Integer,
                     ForeignKey('features_files.id', ondelete='CASCADE'),
                     nullable=False)
    features_set_id = Column(Integer, ForeignKey('features_set.id',
                                                 ondelete='CASCADE'),
                             nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

    features_file = relationship('FeaturesFilesAlchemy',
                                 back_populates='features', uselist=False)
    features_set = relationship('FeaturesSetsAlchemy',
                                back_populates='features', uselist=False)
