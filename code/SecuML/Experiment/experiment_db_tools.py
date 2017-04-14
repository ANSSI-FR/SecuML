## SecuML
## Copyright (C) 2016  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

from SecuML.Tools import mysql_tools

def createExperimentsTable(cursor):
    fields = ['id', 'kind', 'name', 'label_id', 'parent']
    types = ['INT UNSIGNED', 'VARCHAR(200)', 'VARCHAR(1000)',
            'INT UNSIGNED', 'INT UNSIGNED']
    mysql_tools.createTableFromFields(cursor, 'Experiments',
            fields, types, ['id'], auto_increment = True)

def createExperimentsLabelsTable(cursor):
    fields = ['id', 'label']
    types = ['INT UNSIGNED', 'VARCHAR(1000)']
    mysql_tools.createTableFromFields(cursor, 'ExperimentsLabels',
            fields, types, ['id'], auto_increment = True)

def addExperimentLabel(cursor, experiment_label):
    types = ['INT UNSIGNED', 'VARCHAR(1000)']
    values = [0, experiment_label]
    mysql_tools.insertRowIntoTable(cursor, 'ExperimentsLabels',
            values, types)
    experiment_label_id = mysql_tools.getLastInsertedId(cursor)
    return experiment_label_id

def getExperiments(cursor, exp_kind = None):
    query  = 'SELECT name from Experiments'
    if exp_kind is not None:
        query += ' WHERE kind = "' + exp_kind + '"'
        query += ' AND parent IS NULL'
    query += ';'
    cursor.execute(query)
    experiments = [x[0] for x in cursor.fetchall()]
    return experiments

def getExperimentId(cursor, experiment_name):
    cursor.execute('SELECT id \
            FROM Experiments \
            WHERE name = %s', (experiment_name, ))
    return cursor.fetchone()[0]

def getExperimentName(cursor, experiment_id):
    cursor.execute('SELECT name \
            FROM Experiments \
            WHERE id = %s', (experiment_id, ))
    return cursor.fetchone()[0]

def getChildren(cursor, experiment_id):
    cursor.execute('SELECT id \
            FROM Experiments \
            WHERE parent = %s',
            (experiment_id, ))
    return [x[0] for x in cursor.fetchall()]

def getChildExperimentId(cursor, parent_id, child_name):
    cursor.execute('SELECT id '
                   'FROM Experiments '
                   'WHERE parent = %s '
                   'AND name = %s',
                   (parent_id, child_name))
    return cursor.fetchone()[0]
