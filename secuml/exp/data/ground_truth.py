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

from . import compute_hash
from secuml.exp.tools.db_tables import call_specific_db_func
from secuml.exp.tools.db_tables import DatasetsAlchemy
from secuml.exp.tools.exp_exceptions import UpdatedFile


class GroundTruth(object):

    def __init__(self, dataset_conf, secuml_conf, session, cursor):
        self.dataset_conf = dataset_conf
        self.secuml_conf = secuml_conf
        self.session = session
        self.cursor = cursor
        self.exists = None

    def load(self):
        filepath, _ = self.get_filepath_hash()
        self.exists = filepath is not None
        if not self.exists:
            return
        call_specific_db_func(self.secuml_conf.db_type, 'load_ground_truth',
                              (self.cursor, filepath,
                               self.dataset_conf.dataset_id))
        self.secuml_conf.logger.info('Ground-truth file for the dataset %s/%s '
                                     'loaded into the database (%s).'
                                     % (self.dataset_conf.project,
                                        self.dataset_conf.dataset,
                                        filepath))

    def check(self):
        filepath, curr_hash = self.get_filepath_hash()
        self.exists = filepath is not None
        if not self.exists:
            self.secuml_conf.logger.warning('No ground-truth available for '
                                            'the dataset %s/%s.'
                                            % (self.dataset_conf.project,
                                               self.dataset_conf.dataset))
            return
        dataset_id = self.dataset_conf.dataset_id
        query = self.session.query(DatasetsAlchemy)
        query = query.filter(DatasetsAlchemy.id == dataset_id)
        res = query.one()
        ground_truth_hash = res.ground_truth_hash
        if ground_truth_hash != curr_hash:
            raise UpdatedFile(filepath, self.dataset_conf.dataset)

    def get_filepath_hash(self):
        input_dir = self.dataset_conf.input_dir(self.secuml_conf)
        filepath = path.join(input_dir, 'annotations', 'ground_truth.csv')
        if not path.isfile(filepath):
            return None, None
        return filepath, compute_hash(filepath)
