# SecuML
# Copyright (C) 2018  ANSSI
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


def loadIdents(cursor, filename, dataset_id):
    timestamps = False
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        if len(header) == 3:
            timestamps = True
    query = 'CREATE TEMPORARY TABLE instances_import('
    query += 'user_instance_id integer, '
    query += 'ident varchar(200), '
    query += 'timestamp timestamp DEFAULT null,'
    query += 'dataset_id integer DEFAULT ' + str(dataset_id) + ','
    query += 'row_number serial PRIMARY KEY'
    query += ');'
    cursor.execute(query)
    with open(filename, 'r') as f:
        query = 'COPY instances_import'
        if timestamps:
            query += '(user_instance_id,ident,timestamp) '
        else:
            query += '(user_instance_id,ident) '
        query += 'FROM STDIN '
        query += 'WITH CSV HEADER DELIMITER AS \',\' ;'
        cursor.copy_expert(sql=query, file=f)
    query = 'INSERT INTO instances'
    query += '(user_instance_id,ident,timestamp,dataset_id,row_number) '
    query += 'SELECT user_instance_id, ident, timestamp, '
    query += 'dataset_id, row_number '
    query += 'FROM instances_import;'
    cursor.execute(query)

def loadGroundTruth(cursor, filename, families, dataset_id):
    query = 'CREATE TEMPORARY TABLE ground_truth_import('
    query += 'user_instance_id integer PRIMARY KEY, '
    query += 'label ground_truth_enum, '
    query += 'family varchar(200) DEFAULT \'other\', '
    query += 'dataset_id integer DEFAULT ' + \
        str(dataset_id) + ', '
    query += 'id integer DEFAULT NULL'
    query += ');'
    cursor.execute(query)

    with open(filename, 'r') as f:
        query = 'COPY ground_truth_import'
        if families:
            query += '(user_instance_id,label,family) '
        else:
            query += '(user_instance_id,label) '
        query += 'FROM STDIN '
        query += 'WITH CSV HEADER DELIMITER AS \',\' ;'
        cursor.copy_expert(sql=query, file=f)

    query = 'UPDATE ground_truth_import AS t '
    query += 'SET id = i.id '
    query += 'FROM instances AS i '
    query += 'WHERE i.user_instance_id = t.user_instance_id '
    query += 'AND i.dataset_id = t.dataset_id;'
    cursor.execute(query)

    query = 'INSERT INTO ground_truth'
    query += '(instance_id, dataset_id, label, family) '
    query += 'SELECT t.id, t.dataset_id, t.label, t.family '
    query += 'FROM ground_truth_import AS t;'
    cursor.execute(query)

def loadPartialAnnotations(cursor, filename, families, annotations_id,
                           dataset_id):
    query = 'CREATE TEMPORARY TABLE annotations_import('
    query += 'instance_id integer, '
    query += 'annotations_id integer DEFAULT ' + \
        str(annotations_id) + ', '
    query += 'user_instance_id integer, '
    query += 'label labels_enum, '
    query += 'family varchar(200) DEFAULT \'other\', '
    query += 'iteration integer DEFAULT 0, '
    query += 'method varchar(200) DEFAULT \'init\''
    query += ');'
    cursor.execute(query)

    with open(filename, 'r') as f:
        if families:
            query = 'COPY annotations_import(user_instance_id,label,family) '
        else:
            query = 'COPY annotations_import(user_instance_id,label) '
        query += 'FROM STDIN '
        query += 'WITH CSV HEADER DELIMITER AS \',\' ;'
        cursor.copy_expert(sql=query, file=f)

    query = 'UPDATE annotations_import AS l '
    query += 'SET instance_id = i.id '
    query += 'FROM instances AS i '
    query += 'WHERE i.user_instance_id = l.user_instance_id '
    query += 'AND i.dataset_id = ' + str(dataset_id) + ';'
    cursor.execute(query)

    query = 'INSERT INTO annotations'
    query += '(instance_id,annotations_id,label,family,iteration,method) '
    query += 'SELECT instance_id,annotations_id,label,family,iteration,method '
    query += 'FROM annotations_import;'
    cursor.execute(query)
