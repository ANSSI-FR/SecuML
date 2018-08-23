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

from SecuML.core.Tools import dir_tools

from SecuML.experiments import db_tables
from SecuML.experiments.Tools import dir_exp_tools
from SecuML.experiments.Tools import mysql_specific
from SecuML.experiments.Tools import postgresql_specific
from SecuML.experiments.Tools.exp_exceptions import SecuMLexpException


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


class IdentsFileNotFound(SecuMLexpException):

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return('The idents file %s does not exist.'
                % self.filename)


class UpdatedFile(SecuMLexpException):

    def __init__(self, filename, dataset):
        self.filename = filename
        self.dataset  = dataset

    def __str__(self):
        return('The file %s has been updated '
               'since the dataset %s has been loaded.'
               % (self.filename, self.dataset))


class Dataset(object):

    def __init__(self, secuml_conf, session, project, dataset):
        self.secuml_conf = secuml_conf
        self.setSession(session)
        self.project = project
        self.dataset = dataset

    def __del__(self):
        self.session.close()

    def setSession(self, session):
        self.session = session
        self.raw_connection = self.session.connection().connection
        self.cursor = self.raw_connection.cursor()

    def load(self, logger):
        self.checkInputProjectDatasetDir(logger)
        self.loadInDatabase(logger)
        self.raw_connection.commit()

    def checkInputProjectDatasetDir(self, logger):
        # Check project directory
        project_dir = dir_exp_tools.getProjectDirectory(self.secuml_conf,
                                                        self.project)
        if not path.isdir(project_dir):
            raise ProjectDirNotFound(self.secuml_conf.input_data_dir,
                                     self.project)
        # Check dataset directory
        dataset_dir = dir_exp_tools.getDatasetDirectory(self.secuml_conf,
                                                        self.project,
                                                        self.dataset)
        if not path.isdir(dataset_dir):
            raise DatasetDirNotFound(self.secuml_conf.input_data_dir,
                                     self.project,
                                     self.dataset)
        # Check idents file
        self.idents_filename = dir_exp_tools.getIdentsFilename(self.secuml_conf,
                                                          self.project,
                                                          self.dataset)
        if not path.isfile(self.idents_filename):
            raise IdentsFileNotFound(self.idents_filename)
        # Check ground-truth file
        self.annotations_filename = dir_exp_tools.getGroundTruthFilename(
                                            self.secuml_conf,
                                            self.project,
                                            self.dataset)
        if not dir_tools.checkFileExists(self.annotations_filename):
            logger.warning('No ground-truth available for the dataset %s/%s.'
                           % (self.project, self.dataset))
            self.annotations_filename = None

    def remove(self):
        db_tables.removeDataset(self.session, self.project, self.dataset)
        dir_exp_tools.removeDatasetOutputDirectory(self.secuml_conf,
                                                   self.project,
                                                   self.dataset)

    def loadInDatabase(self, logger):
        self.project_id = db_tables.checkProject(self.session, self.project)
        if self.project_id is None:
            self.project_id = db_tables.addProject(self.session, self.project)
        self.dataset_id = db_tables.checkDataset(self.session,
                                                 self.project_id,
                                                 self.dataset)
        self.computeHashes()
        if self.dataset_id is None:
            self.dataset_id = db_tables.addDataset(self.session,
                                                   self.project_id,
                                                   self.dataset,
                                                   self.idents_hash,
                                                   self.ground_truth_hash)
            self.loadIdents(logger)
            if self.annotations_filename is not None:
                self.loadGroundTruth(logger)
        else:
            idents_hash, ground_truth_hash = db_tables.getDatasetHashes(
                            self.session,
                            self.project_id,
                            self.dataset_id)
            self.checkHashes(idents_hash, ground_truth_hash)
            if self.annotations_filename is not None:
                if ground_truth_hash is None:
                    self.loadGroundTruth(logger)

    def checkHashes(self, idents_hash, ground_truth_hash):
        if idents_hash != self.idents_hash:
            raise UpdatedFile(self.idents_filename, self.dataset)
        if self.annotations_filename is not None:
            if ground_truth_hash is not None:
                if ground_truth_hash != self.ground_truth_hash:
                    raise UpdatedFile(self.annotations_filename, self.dataset)

    def computeHashes(self):
        self.idents_hash = dir_tools.computeMD5(self.idents_filename)
        self.ground_truth_hash = None
        if self.annotations_filename is not None:
            self.ground_truth_hash = dir_tools.computeMD5(
                    self.annotations_filename)

    def loadIdents(self, logger):
        idents_filename = dir_exp_tools.getIdentsFilename(self.secuml_conf,
                                                          self.project,
                                                          self.dataset)
        if self.secuml_conf.db_type == 'mysql':
            mysql_specific.loadIdents(self.cursor, idents_filename,
                                      self.dataset_id)
        elif self.secuml_conf.db_type == 'postgresql':
            postgresql_specific.loadIdents(self.cursor, idents_filename,
                                           self.dataset_id)
        logger.info('Idents file for the dataset %s/%s loaded '
                    'into the database (%s).'
                    % (self.project,
                       self.dataset,
                       self.idents_filename))

    def loadGroundTruth(self, logger):
        families = dir_exp_tools.annotationsWithFamilies(
                                        self.annotations_filename)
        if self.secuml_conf.db_type == 'mysql':
            mysql_specific.loadGroundTruth(self.cursor,
                                           self.annotations_filename,
                                           families,
                                           self.dataset_id)
        elif self.secuml_conf.db_type == 'postgresql':
            postgresql_specific.loadGroundTruth(self.cursor,
                                                self.annotations_filename,
                                                families,
                                                self.dataset_id)
        else:
            assert(False)
        logger.info('Ground-truth file for the dataset %s/%s loaded '
                    'into the database (%s).'
                    % (self.project,
                       self.dataset,
                       self.annotations_filename))
