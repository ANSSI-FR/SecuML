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

import csv


def annotations_with_families(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        return len(header) == 3


def load_idents(cursor, filename, dataset_id):
    timestamps = False
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        if len(header) == 3:
            timestamps = True
    cursor.execute('CREATE TEMPORARY TABLE instances_import('
                   'user_instance_id integer, '
                   'ident text, '
                   'timestamp timestamp DEFAULT null,'
                   'dataset_id integer DEFAULT %d,'
                   'row_number serial PRIMARY KEY);' % dataset_id)
    with open(filename, 'r') as f:
        fields = ['user_instance_id', 'ident']
        if timestamps:
            fields.append('timestamp')
        cursor.copy_expert(sql='COPY instances_import(%s) '
                               'FROM STDIN '
                               'WITH CSV HEADER DELIMITER AS \',\' ;'
                               % ','.join(fields),
                           file=f)
    cursor.execute('INSERT INTO instances'
                   '(user_instance_id,ident,timestamp,dataset_id,row_number) '
                   'SELECT user_instance_id, ident, timestamp, '
                   'dataset_id, row_number '
                   'FROM instances_import;')
    cursor.execute('DROP TABLE instances_import;')


def load_ground_truth(cursor, filename, dataset_id):
    families = annotations_with_families(filename)
    cursor.execute('CREATE TEMPORARY TABLE ground_truth_import('
                   'user_instance_id integer PRIMARY KEY, '
                   'label ground_truth_enum, '
                   'family varchar(200) DEFAULT \'other\', '
                   'dataset_id integer DEFAULT %d, '
                   'id integer DEFAULT NULL);' % dataset_id)
    with open(filename, 'r') as f:
        fields = ['user_instance_id', 'label']
        if families:
            fields.append('family')
        cursor.copy_expert(sql='COPY ground_truth_import(%s)'
                               'FROM STDIN '
                               'WITH CSV HEADER DELIMITER AS \',\' ;'
                               % ','.join(fields),
                           file=f)
    cursor.execute('UPDATE ground_truth_import AS t '
                   'SET id = i.id '
                   'FROM instances AS i '
                   'WHERE i.user_instance_id = t.user_instance_id '
                   'AND i.dataset_id = t.dataset_id;')
    cursor.execute('INSERT INTO ground_truth'
                   '(instance_id, dataset_id, label, family) '
                   'SELECT t.id, t.dataset_id, t.label, t.family '
                   'FROM ground_truth_import AS t;')
    cursor.execute('DROP TABLE ground_truth_import;')


def load_partial_annotations(cursor, filename, annotations_id, dataset_id):
    families = annotations_with_families(filename)
    cursor.execute('CREATE TEMPORARY TABLE annotations_import('
                   'instance_id integer, '
                   'annotations_id integer DEFAULT %d, '
                   'user_instance_id integer, '
                   'label labels_enum, '
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
