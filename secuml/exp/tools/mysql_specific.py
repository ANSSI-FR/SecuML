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


from .postgresql_specific import annotations_with_families


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
    cursor.execute('LOAD DATA LOCAL INFILE \'%s\' '
                   'INTO TABLE instances '
                   'CHARACTER SET UTF8 '
                   'FIELDS TERMINATED BY \',\' '
                   'OPTIONALLY ENCLOSED BY \'"\' '
                   'LINES TERMINATED BY \'%s\' '
                   'IGNORE 1 LINES '
                   'SET dataset_id = %d,'
                   'row_number = NULL;'
                   % (filename,
                      get_trailing_characters(filename),
                      dataset_id))
    cursor.execute('SET @pos = 0;')
    cursor.execute('UPDATE instances SET row_number = '
                   '( SELECT @pos := @pos + 1 ) WHERE dataset_id = %d;'
                   % dataset_id)


def load_ground_truth(cursor, filename, dataset_id):
    families = annotations_with_families(filename)
    cursor.execute('CREATE TEMPORARY TABLE ground_truth_import('
                   'user_instance_id integer PRIMARY KEY, '
                   'label varchar(200), '
                   'family varchar(200) DEFAULT \'other\', '
                   'dataset_id integer DEFAULT %d, '
                   'id integer DEFAULT NULL);' % dataset_id)
    fields = ['user_instance_id', 'label']
    if families:
        fields.append('family')
    cursor.execute('LOAD DATA LOCAL INFILE \'%s\' '
                   'INTO TABLE ground_truth_import '
                   'FIELDS TERMINATED BY \',\' '
                   'LINES TERMINATED BY \'%s\' '
                   'IGNORE 1 LINES '
                   '(%s);' % (filename,
                              get_trailing_characters(filename),
                              ','.join(fields)))
    cursor.execute('UPDATE ground_truth_import t '
                   'JOIN instances i '
                   'ON i.user_instance_id = t.user_instance_id '
                   'AND i.dataset_id = t.dataset_id '
                   'SET t.id = i.id;')
    cursor.execute('INSERT INTO ground_truth'
                   '(instance_id, dataset_id, label, family) '
                   'SELECT t.id, t.dataset_id, t.label, t.family '
                   'FROM ground_truth_import AS t;')
    cursor.execute('DROP TABLE ground_truth_import;')


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
