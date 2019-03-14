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
from secuml.exp.tools.db_tables import DatasetsAlchemy
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

    def load(self):
        filepath, _ = self.get_filepath_hash()
        if self.secuml_conf.db_type == 'mysql':
            mysql_specific.load_idents(self.cursor, filepath,
                                       self.dataset_conf.dataset_id)
        elif self.secuml_conf.db_type == 'postgresql':
            postgresql_specific.load_idents(self.cursor, filepath,
                                            self.dataset_conf.dataset_id)
        else:
            assert(False)
        self.secuml_conf.logger.info('Idents file for the dataset %s/%s '
                                     'loaded into the database (%s).'
                                     % (self.dataset_conf.project,
                                        self.dataset_conf.dataset,
                                        filepath))

    def check(self):
        filepath, curr_idents_hash = self.get_filepath_hash()
        dataset_id = self.dataset_conf.dataset_id
        query = self.session.query(DatasetsAlchemy)
        query = query.filter(DatasetsAlchemy.id == dataset_id)
        idents_hash = query.one().idents_hash
        if idents_hash != curr_idents_hash:
            raise UpdatedFile(filepath, self.dataset_conf.dataset)

    def get_filepath_hash(self):
        input_dir = self.dataset_conf.input_dir(self.secuml_conf)
        filepath = path.join(input_dir, 'idents.csv')
        if not path.isfile(filepath):
            raise IdentsFileNotFound(filepath)
        return filepath, compute_hash(filepath)
