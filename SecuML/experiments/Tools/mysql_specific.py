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


def loadIdents(cursor, filename, dataset_id):
    query = 'LOAD DATA LOCAL INFILE \'' + filename + '\' '
    query += 'INTO TABLE ' + 'instances' + ' '
    query += 'CHARACTER SET UTF8 '
    query += 'FIELDS TERMINATED BY \',\' '
    query += 'OPTIONALLY ENCLOSED BY \'"\' '
    query += 'IGNORE 1 LINES '
    query += 'SET dataset_id = ' + str(dataset_id) + ','
    query += 'row_number = NULL'
    query += ';'
    cursor.execute(query)
    query = 'SET @pos = 0;'
    cursor.execute(query)
    query = 'UPDATE instances SET row_number = '
    query += '( SELECT @pos := @pos + 1 ) WHERE dataset_id = ' + \
        str(dataset_id)
    query += ';'
    cursor.execute(query)

def loadGroundTruth(cursor, filename, families, dataset_id):
    query = 'CREATE TEMPORARY TABLE ground_truth_import('
    query += 'user_instance_id integer PRIMARY KEY, '
    query += 'label varchar(200), '
    query += 'family varchar(200) DEFAULT \'other\', '
    query += 'dataset_id integer DEFAULT ' + \
        str(dataset_id) + ', '
    query += 'id integer DEFAULT NULL'
    query += ');'
    cursor.execute(query)

    query = 'LOAD DATA LOCAL INFILE \'' + filename + '\' '
    query += 'INTO TABLE ' + 'ground_truth_import' + ' '
    query += 'FIELDS TERMINATED BY \',\' '
    query += 'IGNORE 1 LINES '
    if families:
        query += '(user_instance_id, label, family) '
    else:
        query += '(user_instance_id, label) '
    query += ';'
    cursor.execute(query)

    query = 'UPDATE ground_truth_import t '
    query += 'JOIN instances i '
    query += 'ON i.user_instance_id = t.user_instance_id '
    query += 'AND i.dataset_id = t.dataset_id '
    query += 'SET t.id = i.id;'
    cursor.execute(query)

    query = 'INSERT INTO ground_truth'
    query += '(instance_id, dataset_id, label, family) '
    query += 'SELECT t.id, t.dataset_id, t.label, t.family '
    query += 'FROM ground_truth_import AS t;'
    cursor.execute(query)

    query = 'DROP TABLE ground_truth_import;'
    cursor.execute(query)

def loadPartialAnnotations(cursor, filename, families, annotations_id,
                           dataset_id):
    query = 'CREATE TEMPORARY TABLE labels_import('
    query += 'instance_id integer, '
    query += 'annotations_id integer DEFAULT ' + \
        str(annotations_id) + ', '
    query += 'user_instance_id integer, '
    query += 'label varchar(200), '
    query += 'family varchar(200) DEFAULT \'other\', '
    query += 'iteration integer DEFAULT 0, '
    query += 'method varchar(200) DEFAULT \'init\''
    query += ');'
    cursor.execute(query)

    query = 'LOAD DATA LOCAL INFILE \'' + filename + '\' '
    query += 'INTO TABLE ' + 'labels_import' + ' '
    query += 'FIELDS TERMINATED BY \',\' '
    query += 'IGNORE 1 LINES '
    if families:
        query += '(user_instance_id, label, family) '
    else:
        query += '(user_instance_id, label) '
    query += ';'
    cursor.execute(query)

    query = 'UPDATE labels_import l '
    query += 'JOIN instances i '
    query += 'ON i.user_instance_id = l.user_instance_id '
    query += 'AND i.dataset_id = ' + str(dataset_id) + ' '
    query += 'SET l.instance_id = i.id;'
    cursor.execute(query)

    query = 'INSERT INTO annotations(instance_id,annotations_id,label,family,iteration,method) '
    query += 'SELECT instance_id,annotations_id,label,family,iteration,method '
    query += 'FROM labels_import;'
    cursor.execute(query)
