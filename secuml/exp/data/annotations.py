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

from secuml.exp.conf.annotations import AnnotationsTypes
from secuml.exp.tools.db_tables import call_specific_db_func
from secuml.exp.tools.db_tables import ExpAnnotationsAlchemy
from secuml.exp.tools.exp_exceptions import SecuMLexpException


class Annotations(object):

    def __init__(self, dataset_conf, annotations_conf, secuml_conf, session):
        self.dataset_conf = dataset_conf
        self.annotations_conf = annotations_conf
        self.secuml_conf = secuml_conf
        self.session = session

    def load(self):
        annotations_id = self.annotations_conf.annotations_id
        annotations_type = self.annotations_conf.annotations_type
        filename = self.annotations_conf.annotations_filename
        if annotations_id is None:
            annotations_id = self.add_exp_annotations_in_db()
            if annotations_type == AnnotationsTypes.partial:
                self.load_partial_annotations(filename, annotations_id)
        else:
            annotations_type = self.get_annotations_type(annotations_id)
        self.annotations_conf.set_exp_annotations(annotations_id,
                                                  annotations_type)

    def add_exp_annotations_in_db(self):
        annotations_type = self.annotations_conf.annotations_type
        exp_annotations = ExpAnnotationsAlchemy(type=annotations_type.name)
        self.session.add(exp_annotations)
        self.session.flush()
        return exp_annotations.id

    def load_partial_annotations(self, filename, annotations_id):
        filename = path.join(self.dataset_conf.input_dir(self.secuml_conf),
                             'annotations', filename)
        if not path.isfile(filename):
            raise SecuMLexpException('The annotations file %s does not exist.'
                                     % filename)
        conn = self.session.connection().connection
        cursor = conn.cursor()
        call_specific_db_func(self.secuml_conf.db_type,
                              'load_partial_annotations',
                              (cursor, filename, annotations_id,
                               self.dataset_conf.dataset_id))
        self.session.flush()

    def get_annotations_type(self, annotations_id):
        query = self.session.query(ExpAnnotationsAlchemy)
        query = query.filter(ExpAnnotationsAlchemy.id == annotations_id)
        exp_annotations = query.one()
        return AnnotationsTypes[exp_annotations.type]
