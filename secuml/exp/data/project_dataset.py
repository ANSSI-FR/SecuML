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

import os.path as path
from sqlalchemy.orm.exc import NoResultFound

from secuml.exp.tools.db_tables import DatasetsAlchemy
from secuml.exp.tools.db_tables import FeaturesSetsAlchemy
from secuml.exp.tools.db_tables import ExpAlchemy
from secuml.exp.tools.db_tables import ExpRelationshipsAlchemy
from secuml.exp.tools.exp_exceptions import SecuMLexpException

from .idents import Idents


class ProjectDirNotFound(SecuMLexpException):

    def __init__(self, input_data_dir, project):
        self.input_data_dir = input_data_dir
        self.project = project

    def __str__(self):
        return('The project directory %s cannot be found in the '
               'input_data_dir %s.'
               % (self.project, self.input_data_dir))


class DatasetDirNotFound(SecuMLexpException):

    def __init__(self, input_data_dir, project, dataset):
        self.input_data_dir = input_data_dir
        self.project = project
        self.dataset = dataset

    def __str__(self):
        return('The dataset directory %s cannot be found in the '
               'directory %s.'
               % (self.dataset, path.join(self.input_data_dir,
                                          self.project)))


class UndefinedProject(SecuMLexpException):

    def __init__(self, project):
        self.project = project

    def __str__(self):
        return('There is no experiment for the project %s.' % self.project)


def rm_project_from_db(session, project):
    # Check whether the project exists.
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.project == project)
    if query.first() is None:
        raise UndefinedProject(project)
    # Delete all the links between the experiments for the project
    query = session.query(ExpAlchemy.id)
    query = query.join(ExpAlchemy.features_set)
    query = query.join(FeaturesSetsAlchemy.dataset)
    query = query.filter(DatasetsAlchemy.project == project)
    all_exps = [x[0] for x in query.all()]
    query = session.query(ExpRelationshipsAlchemy)
    query = query.filter(ExpRelationshipsAlchemy.child_id.in_(all_exps))
    query.delete(synchronize_session='fetch')
    # Delete all the datasets of the project
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.project == project)
    query.delete()
    session.flush()


def get_dataset(session, project, dataset):
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.project == project)
    query = query.filter(DatasetsAlchemy.dataset == dataset)
    try:
        return query.one()
    except NoResultFound:
        return None


class ProjectDataset(object):

    def __init__(self, dataset_conf, secuml_conf, session):
        self._set_var(dataset_conf, secuml_conf, session)
        self.idents = Idents(self.dataset_conf, self.secuml_conf, self.session,
                             self.cursor)

    def _set_var(self, dataset_conf, secuml_conf, session):
        # Configuration
        self.secuml_conf = secuml_conf
        self.dataset_conf = dataset_conf
        self.project = dataset_conf.project
        self.dataset = dataset_conf.dataset
        # Session
        self.session = session
        self.raw_connection = self.session.connection().connection
        self.cursor = self.raw_connection.cursor()

    def load(self):
        self._check_input_dataset_dir()
        self._set_dataset_id()
        return self.idents.num_instances()

    def _check_input_dataset_dir(self):
        # Check project directory
        project_dir = path.join(self.secuml_conf.input_data_dir, self.project)
        if not path.isdir(project_dir):
            raise ProjectDirNotFound(self.secuml_conf.input_data_dir,
                                     self.project)
        # Check dataset directory
        dataset_dir = path.join(project_dir, self.dataset)
        if not path.isdir(dataset_dir):
            raise DatasetDirNotFound(self.secuml_conf.input_data_dir,
                                     self.project, self.dataset)

    def _set_dataset_id(self):
        dataset_obj = get_dataset(self.session, self.project, self.dataset)
        if dataset_obj is not None:
            self.dataset_id = dataset_obj.id
            self.dataset_conf.set_dataset_id(self.dataset_id, self.session)
            self.dataset_conf.set_has_ground_truth(dataset_obj.ground_truth)
            self.idents.check()
        else:
            # Add dataset to DB
            _, idents_hash = self.idents.get_filepath_hash()
            dataset = DatasetsAlchemy(project=self.project,
                                      dataset=self.dataset,
                                      idents_hash=idents_hash)
            self.session.add(dataset)
            self.session.flush()
            self.dataset_id = dataset.id
            self.dataset_conf.set_dataset_id(self.dataset_id, self.session)
            # Load idents (idents, timestamps, ground truth labels/families)
            has_ground_truth = self.idents.load()
            self.dataset_conf.set_has_ground_truth(has_ground_truth)
            dataset.ground_truth = has_ground_truth
            self.session.flush()
