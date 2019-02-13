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

from . import compute_hash
from secuml.exp.tools.db_tables import DatasetsHashesAlchemy
from secuml.exp.tools import mysql_specific
from secuml.exp.tools import postgresql_specific
from secuml.exp.tools.exp_exceptions import SecuMLexpException
from secuml.exp.tools.exp_exceptions import UpdatedFile


class IdentsFileNotFound(SecuMLexpException):

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'The idents file %s does not exist.' % self.filename


class Idents(object):

    def __init__(self, dataset_conf, secuml_conf, session, cursor):
        self.dataset_conf = dataset_conf
        self.secuml_conf = secuml_conf
        self.session = session
        self.cursor = cursor

    def load(self, already_loaded):
        self._check(already_loaded)
        if not already_loaded:
            self._add_to_db()

    def _check(self, already_loaded):
        # Check whether the file exists
        input_dir = self.dataset_conf.input_dir(self.secuml_conf)
        self.filepath = path.join(input_dir, 'idents.csv')
        if not path.isfile(self.filepath):
            raise IdentsFileNotFound(self.filepath)
        # Check the hash
        self.idents_hash = compute_hash(self.filepath)
        dataset_id = self.dataset_conf.dataset_id
        if already_loaded:
            query = self.session.query(DatasetsHashesAlchemy)
            query = query.filter(DatasetsHashesAlchemy.id == dataset_id)
            idents_hash = query.one().idents_hash
            if idents_hash != self.idents_hash:
                raise UpdatedFile(self.filepath, self.dataset_conf.dataset)

    def _add_to_db(self):
        if self.secuml_conf.db_type == 'mysql':
            mysql_specific.load_idents(self.cursor, self.filepath,
                                       self.dataset_conf.dataset_id)
        elif self.secuml_conf.db_type == 'postgresql':
            postgresql_specific.load_idents(self.cursor, self.filepath,
                                            self.dataset_conf.dataset_id)
        else:
            assert(False)
        self.secuml_conf.logger.info('Idents file for the dataset %s/%s loaded '
                                     'into the database (%s).'
                                     % (self.dataset_conf.project,
                                        self.dataset_conf.dataset,
                                        self.filepath))
