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

import sqlalchemy
from sqlalchemy.sql.expression import func

from secuml.exp.tools import annotations_with_families
from secuml.exp.tools import idents_header_info


def load_idents(cursor, filename, dataset_id):
    has_timestamp, gt_labels, gt_families = idents_header_info(filename)
    fields = ['user_instance_id', 'ident']
    if has_timestamp:
        fields.append('timestamp')
    if gt_labels:
        fields.append('label')
        if gt_families:
            fields.append('family')
    cursor.execute('CREATE TEMPORARY TABLE instances_import('
                   'user_instance_id integer, '
                   'ident text, '
                   'timestamp timestamp DEFAULT null, '
                   'label boolean default null, '
                   'family char(200) default null, '
                   'dataset_id integer DEFAULT %d,'
                   'row_number serial PRIMARY KEY);' % dataset_id)
    with open(filename, 'r') as f:
        cursor.copy_expert(sql='COPY instances_import(%s) '
                               'FROM STDIN '
                               'WITH CSV HEADER DELIMITER AS \',\' ;'
                               % ','.join(fields),
                           file=f)
    cursor.execute('INSERT INTO instances'
                   '(user_instance_id,ident,timestamp,label,family,dataset_id,'
                   'row_number) '
                   'SELECT user_instance_id, ident, timestamp, label, family, '
                   'dataset_id, row_number '
                   'FROM instances_import;')
    cursor.execute('DROP TABLE instances_import;')
    return gt_labels


def load_partial_annotations(cursor, filename, annotations_id, dataset_id):
    families = annotations_with_families(filename)
    cursor.execute('CREATE TEMPORARY TABLE annotations_import('
                   'instance_id integer, '
                   'annotations_id integer DEFAULT %d, '
                   'user_instance_id integer, '
                   'label boolean, '
                   'family varchar(200) DEFAULT \'other\', '
                   'iteration integer DEFAULT 0, '
                   'method varchar(200) DEFAULT \'init\''
                   ');' % annotations_id)
    with open(filename, 'r') as f:
        fields = ['user_instance_id', 'label']
        if families:
            fields.append('family')
        cursor.copy_expert(sql='COPY annotations_import(%s) '
                               'FROM STDIN '
                               'WITH CSV HEADER DELIMITER AS \',\' ;'
                               % ','.join(fields),
                           file=f)
    cursor.execute('UPDATE annotations_import AS t '
                   'SET instance_id = i.id '
                   'FROM instances AS i '
                   'WHERE i.user_instance_id = t.user_instance_id '
                   'AND i.dataset_id = %d;' % dataset_id)
    cursor.execute('INSERT INTO annotations'
                   '(instance_id,annotations_id,label,family,iteration,'
                   'method) '
                   'SELECT instance_id,annotations_id,label,family,iteration,'
                   'method '
                   'FROM annotations_import;')
    cursor.execute('DROP TABLE annotations_import;')


def get_engine(db_uri):
    return sqlalchemy.create_engine(db_uri, echo=False)


def random_order(query):
    return query.order_by(func.random())
