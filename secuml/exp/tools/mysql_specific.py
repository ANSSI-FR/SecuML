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


def get_trailing_characters(filename):
    with open(filename, 'rb') as f:
        line = f.readline()
        last = chr(line[-1])
        last_1 = chr(line[-2])
        if last_1 not in ['\n', '\r']:
            return last
        else:
            return last_1 + last


def load_idents(cursor, filename, dataset_id):
    has_timestamp, gt_labels, gt_families = idents_header_info(filename)
    fields = ['user_instance_id', 'ident']
    if has_timestamp:
        fields.append('timestamp')
    if gt_labels:
        fields.append('label')
        if gt_families:
            fields.append('family')
    cursor.execute('LOAD DATA LOCAL INFILE \'%s\' '
                   'INTO TABLE instances '
                   'CHARACTER SET UTF8 '
                   'FIELDS TERMINATED BY \',\' '
                   'OPTIONALLY ENCLOSED BY \'"\' '
                   'LINES TERMINATED BY \'%s\' '
                   'IGNORE 1 LINES '
                   '(%s) '
                   'SET dataset_id = %d,'
                   'row_number = NULL;'
                   % (filename,
                      get_trailing_characters(filename),
                      ','.join(fields),
                      dataset_id))
    cursor.execute('SET @pos = 0;')
    cursor.execute('UPDATE instances SET row_number = '
                   '( SELECT @pos := @pos + 1 ) WHERE dataset_id = %d;'
                   % dataset_id)
    return gt_labels


def load_partial_annotations(cursor, filename, annotations_id, dataset_id):
    families = annotations_with_families(filename)
    cursor.execute('CREATE TEMPORARY TABLE labels_import('
                   'instance_id integer, '
                   'annotations_id integer DEFAULT %d, '
                   'user_instance_id integer, '
                   'label varchar(200), '
                   'family varchar(200) DEFAULT \'other\', '
                   'iteration integer DEFAULT 0, '
                   'method varchar(200) DEFAULT \'init\''
                   ');' % annotations_id)
    fields = ['user_instance_id', 'label']
    if families:
        fields.append('family')
    cursor.execute('LOAD DATA LOCAL INFILE \'%s\' '
                   'INTO TABLE labels_import '
                   'FIELDS TERMINATED BY \',\' '
                   'LINES TERMINATED BY \'%s\' '
                   'IGNORE 1 LINES '
                   '(%s);' % (filename,
                              get_trailing_characters(filename),
                              ','.join(fields)))
    cursor.execute('UPDATE labels_import l '
                   'JOIN instances i '
                   'ON i.user_instance_id = l.user_instance_id '
                   'AND i.dataset_id = %d '
                   'SET l.instance_id = i.id;' % dataset_id)
    cursor.execute('INSERT INTO annotations'
                   '(instance_id,annotations_id,label,family,iteration,'
                   'method) '
                   'SELECT instance_id,annotations_id,label,family,iteration,'
                   'method '
                   'FROM labels_import;')


def get_engine(db_uri):
    return sqlalchemy.create_engine(db_uri + '?charset=utf8', echo=False)


def random_order(query):
    return query.order_by(func.rand())
