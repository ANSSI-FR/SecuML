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

import os.path as path
import shutil
from sqlalchemy.orm.exc import NoResultFound

from secuml.exp.tools.db_tables import DatasetsAlchemy
from secuml.exp.tools.db_tables import DatasetFeaturesAlchemy
from secuml.exp.tools.db_tables import DatasetsHashesAlchemy
from secuml.exp.tools.db_tables import ExpAlchemy
from secuml.exp.tools.db_tables import ExpRelationshipsAlchemy
from secuml.exp.tools.db_tables import ProjectsAlchemy
from secuml.exp.tools.exp_exceptions import SecuMLexpException

from .idents import Idents
from .ground_truth import GroundTruth


def rm_project_from_db(session, project):
    project_id = get_project_id(session, project)
    if project_id is None:
        return
    # Delete all the links between the experiments for the project
    query = session.query(ExpAlchemy.id)
    query = query.join(ExpAlchemy.dataset_features)
    query = query.join(DatasetFeaturesAlchemy.dataset)
    query = query.filter(DatasetsAlchemy.project_id == project_id)
    all_exps = [x[0] for x in query.all()]
    query = session.query(ExpRelationshipsAlchemy)
    query = query.filter(ExpRelationshipsAlchemy.child_id.in_(all_exps))
    query.delete(synchronize_session='fetch')
    # Delete the project
    query = session.query(ProjectsAlchemy)
    query = query.filter(ProjectsAlchemy.id == project_id)
    row = query.one()
    session.delete(row)
    session.flush()


def get_project_id(session, project):
    query = session.query(ProjectsAlchemy)
    query = query.filter(ProjectsAlchemy.project == project)
    try:
        return query.one().id
    except NoResultFound:
        return None


def get_dataset_id(session, project_id, dataset):
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.project_id == project_id)
    query = query.filter(DatasetsAlchemy.dataset == dataset)
    try:
        return query.one().id
    except NoResultFound:
        return None


def get_project_dataset_ids(session, project, dataset):
    project_id = get_project_id(session, project)
    dataset_id = None
    if project_id is not None:
        dataset_id = get_dataset_id(session, project_id, dataset)
    return project_id, dataset_id


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


class ProjectDataset(object):

    def __init__(self, dataset_conf, secuml_conf, session):
        self._set_var(dataset_conf, secuml_conf, session)
        self.idents = Idents(self.dataset_conf, self.secuml_conf, self.session,
                             self.cursor)
        self.ground_truth = GroundTruth(self.dataset_conf, self.secuml_conf,
                                        self.session, self.cursor)

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
        self._check_already_loaded()
        self.idents.load(self.already_loaded)
        self.ground_truth.load(self.already_loaded)
        if not self.already_loaded:
            self._add_hashes_to_db()
        self.already_loaded = True

    def _rm_dataset_from_db(self):
        project_id, dataset_id = get_project_dataset_ids(self.session,
                                                         self.project,
                                                         self.dataset)
        if project_id is None or dataset_id is None:
            return
        query = self.session.query(DatasetsAlchemy)
        query = query.filter(DatasetsAlchemy.id == dataset_id)
        row = query.one()
        self.session.delete(row)
        self.session.flush()

    def remove(self):
        self._rm_dataset_from_db()
        dataset_ouput_dir = self.dataset_conf.output_dir(self.secuml_conf)
        if path.isdir(dataset_ouput_dir):
            shutil.rmtree(dataset_ouput_dir)

    def _add_hashes_to_db(self):
        idents_hash = self.idents.idents_hash
        ground_truth_hash = None
        if self.dataset_conf.has_ground_truth:
            ground_truth_hash = self.ground_truth.ground_truth_hash
        row = DatasetsHashesAlchemy(id=self.dataset_conf.dataset_id,
                                    idents_hash=idents_hash,
                                    ground_truth_hash=ground_truth_hash)
        self.session.add(row)
        self.session.flush()

    def _add_dataset_to_db(self):
        dataset = DatasetsAlchemy(project_id=self.project_id,
                                  dataset=self.dataset)
        self.session.add(dataset)
        self.session.flush()
        return dataset.id

    def _add_project_to_db(self):
        project = ProjectsAlchemy(project=self.project)
        self.session.add(project)
        self.session.flush()
        return project.id

    def _check_already_loaded(self):
        self.project_id, self.dataset_id = get_project_dataset_ids(self.session,
                                                                   self.project,
                                                                   self.dataset)
        self.already_loaded = (self.project_id is not None and
                               self.dataset_id is not None)
        if self.project_id is None:
            self.project_id = self._add_project_to_db()
        if self.dataset_id is None:
            self.dataset_id = self._add_dataset_to_db()
        self.dataset_conf.set_dataset_id(self.dataset_id, self.session)

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
