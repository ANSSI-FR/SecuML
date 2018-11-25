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
from SecuML.exp.tools import mysql_specific
from SecuML.exp.tools import postgresql_specific
from SecuML.exp.tools.exp_exceptions import UpdatedFile


class GroundTruth(object):

    def __init__(self, dataset_conf, secuml_conf, session, cursor):
        self.dataset_conf = dataset_conf
        self.secuml_conf = secuml_conf
        self.session = session
        self.cursor = cursor

    def load(self, already_loaded):
        self._check(already_loaded)
        self.dataset_conf.set_has_ground_truth(self.filepath is not None)
        if not already_loaded and self.filepath is not None:
            self._add_to_db()

    def _check(self, already_loaded):
        # Check whether the file exists
        input_dir = self.dataset_conf.input_dir(self.secuml_conf)
        self.filepath = path.join(input_dir, 'annotations', 'ground_truth.csv')
        if not path.isfile(self.filepath):
            self.secuml_conf.logger.warning('No ground-truth available for the '
                                            'dataset %s/%s.'
                                            % (self.dataset_conf.project,
                                               self.dataset_conf.dataset))
            self.filepath = None
            return
        # Check the hash
        self.ground_truth_hash = dir_tools.compute_hash(self.filepath)
        dataset_id = self.dataset_conf.dataset_id
        if already_loaded:
            query = self.session.query(DatasetsHashesAlchemy)
            query = query.filter(DatasetsHashesAlchemy.id == dataset_id)
            res = query.one()
            ground_truth_hash = res.ground_truth_hash
            if ground_truth_hash != self.ground_truth_hash:
                raise UpdatedFile(self.filepath, self.dataset_conf.dataset)

    def _add_to_db(self):
        if self.secuml_conf.db_type == 'mysql':
            mysql_specific.loadGroundTruth(self.cursor, self.filepath,
                                           self.dataset_conf.dataset_id)
        elif self.secuml_conf.db_type == 'postgresql':
            postgresql_specific.loadGroundTruth(self.cursor, self.filepath,
                                                self.dataset_conf.dataset_id)
        else:
            assert(False)
        self.secuml_conf.logger.info('Ground-truth file for the dataset %s/%s '
                                'loaded into the database (%s).'
                                % (self.dataset_conf.project,
                                   self.dataset_conf.dataset,
                                   self.filepath))
