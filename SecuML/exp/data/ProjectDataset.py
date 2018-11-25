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

from SecuML.core.tools import dir_tools
from SecuML.exp.db_tables import DatasetsHashesAlchemy
from SecuML.exp import db_tables
from SecuML.exp.tools.exp_exceptions import SecuMLexpException

from .Idents import Idents
from .GroundTruth import GroundTruth


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
        #self.session = session
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

    def remove(self):
        db_tables.removeDataset(self.session, self.project, self.dataset)
        dir_tools.removeDirectory(self.dataset_conf.output_dir(self.secuml_conf))

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

    def _check_already_loaded(self):
        self.already_loaded = True
        self.project_id = db_tables.checkProject(self.session, self.project)
        if self.project_id is None:
            self.project_id = db_tables.addProject(self.session, self.project)
            self.already_loaded = False
        self.dataset_id = db_tables.checkDataset(self.session, self.project_id,
                                                 self.dataset)
        if self.dataset_id is None:
            self.already_loaded = False
            self.dataset_id = db_tables.add_dataset(self.session,
                                                    self.project_id,
                                                    self.dataset)
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
