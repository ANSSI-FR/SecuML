## SecuML
## Copyright (C) 2016-2017  ANSSI
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

from SecuML.Data import idents_tools
from SecuML.Tools import mysql_tools

class NoLabel(Exception):
    def __str__(self):
        return ''

def labelBooleanToString(label):
    if label:
        return 'malicious'
    else:
        return 'benign'

def labelStringToBoolean(label):
    return label == 'malicious'

def createLabelsTable(cursor):
    fields  = ['experiment_label_id', 'instance_id']
    fields += ['label', 'family']
    fields += ['iteration', 'method', 'annotation']
    types   = ['INT UNSIGNED', 'INT UNSIGNED', 'VARCHAR(200)']
    types  += ['VARCHAR(200)', 'INT UNSIGNED', 'VARCHAR(200)', 'BIT(1)']
    mysql_tools.createTableFromFields(cursor, 'Labels',
            fields, types, ['experiment_label_id', 'instance_id'])

def hasTrueLabels(cursor):
    cursor.execute('SELECT * FROM ExperimentsLabels \
            WHERE label = %s', ('true_labels',))
    return cursor.fetchone() is not None

def getLabel(cursor, instance_id, experiment_label_id):
    query  = 'SELECT label, family '
    query += 'FROM Labels '
    query += 'WHERE instance_id = ' + str(instance_id) + ' '
    query += 'AND experiment_label_id = ' + str(experiment_label_id)
    query += ';'
    cursor.execute(query)
    row = cursor.fetchone()
    if row is not None:
        label  = row[0]
        family = row[1]
        return label, family
    else:
        return None

def getLabelDetails(cursor, instance_id, experiment_label_id):
    query  = 'SELECT * '
    query += 'FROM Labels '
    query += 'WHERE instance_id = ' + str(instance_id) + ' '
    query += 'AND experiment_label_id = ' + str(experiment_label_id)
    query += ';'
    cursor.execute(query)
    row = cursor.fetchone()
    if row is not None:
        label      = row[2]
        family     = row[3]
        method     = row[5]
        annotation = row[6]
        return label, family, method, annotation
    else:
        raise NoLabel()

def hasAnnotation(cursor, instance_id, experiment_label_id):
    label_details = getLabelDetails(cursor, instance_id, experiment_label_id)
    if label_details is None:
        return False
    else:
        return label_details[3]

def addLabel(cursor, experiment_label_id, instance_id, final_label,
        family, iteration_number, method, annotation):
    types  = ['INT UNSIGNED', 'INT UNSIGNED', 'VARCHAR(200)']
    types += ['VARCHAR(200)', 'INT', 'VARCHAR(200)', 'BIT(1)']
    label_info = [experiment_label_id, instance_id, final_label,
            family, iteration_number, method, annotation]
    mysql_tools.insertRowIntoTable(cursor, 'Labels', label_info, types)

def removeLabel(cursor, experiment_label_id, instance_id):
    if getLabel(cursor, instance_id, experiment_label_id) is not None:
        cursor.execute('DELETE FROM Labels '
                       'WHERE experiment_label_id = %s '
                       'AND instance_id = %s',
                       (experiment_label_id, instance_id,))

def removeExperimentLabels(cursor, experiment_label_id):
    cursor.execute('DELETE FROM Labels WHERE experiment_label_id = %s',
            (experiment_label_id,))
    cursor.execute('DELETE FROM ExperimentsLabels '
                   'WHERE id = %s',
                   (experiment_label_id, ))

def getExperimentLabelsFamilies(cursor, experiment_label_id):
    query  = 'SELECT label, family '
    query += 'FROM Labels '
    query += 'WHERE experiment_label_id = ' + str(experiment_label_id) + ' '
    query += 'ORDER BY instance_id'
    query += ';'
    cursor.execute(query)
    res = cursor.fetchall()
    labels = [labelStringToBoolean(x[0]) for x in res]
    families = [x[1] for x in res]
    return labels, families

def getDatasetFamilies(cursor, project, dataset, experiment_label_id):
    mysql_tools.useDatabase(cursor, project, dataset)
    query  = 'SELECT DISTINCT family FROM Labels '
    query += 'WHERE experiment_label_id = ' + str(experiment_label_id) + ';';
    cursor.execute(query)
    return [s[0] for s in cursor.fetchall()]

def getLabelsFamilies(cursor, experiment_label_id, instance_ids = None,
                      iteration_max = None):
    query  = 'SELECT DISTINCT label, family '
    query += 'FROM Labels '
    query += 'WHERE experiment_label_id = ' + str(experiment_label_id) + ' '
    if instance_ids is not None:
        query += 'AND instance_id IN ('
        query += ','.join(map(str, instance_ids))
        query += ') '
    if iteration_max is not None:
        query += 'AND iteration <= ' + str(iteration_max)
    query += ';'
    cursor.execute(query)
    labels = {}
    row = cursor.fetchone()
    while row is not None:
        label = row[0]
        family = row[1]
        if label not in labels.keys():
            labels[label] = {}
        labels[label][family] = 0
        row = cursor.fetchone()
    return labels

def getFamiliesCounts(cursor, experiment_label_id, iteration_max = None, label = None):
    query  = 'SELECT family, count(*) '
    query += 'FROM Labels '
    query += 'WHERE experiment_label_id = ' + str(experiment_label_id) + ' '
    if iteration_max is not None:
        query += 'AND iteration <= ' + str(iteration_max) + ' '
    if label is not None:
        query += 'AND label = "' + label + '" '
    query += 'GROUP BY family'
    query += ';'
    cursor.execute(query)
    family_counts = {}
    row = cursor.fetchone()
    while row is not None:
        family_counts[row[0]] = row[1]
        row = cursor.fetchone()
    return family_counts

def getLabelFamilyIds(cursor, experiment_label_id, label, family = None,
                      iteration_max = None, instance_ids = None):
    query  = 'SELECT instance_id '
    query += 'FROM Labels '
    query += 'WHERE label = "' + label + '" '
    if family is not None:
        query += 'AND family = "' + family + '" '
    query += 'AND experiment_label_id = ' + str(experiment_label_id) + ' '
    if instance_ids is not None:
        query += 'AND instance_id IN ('
        query += ','.join(map(str, instance_ids))
        query += ') '
    if iteration_max is not None:
        query += 'AND iteration <= ' + str(iteration_max)
    query += ';'
    cursor.execute(query)
    ids = [int(x[0]) for x in cursor.fetchall()]
    return ids

def getUnlabeledIds(cursor, experiment_label_id, instance_ids = None,
        iteration_max = None):
    labeled_ids = getLabeledIds(cursor, experiment_label_id,
            iteration_max = iteration_max)
    if instance_ids is None:
        instance_ids = idents_tools.getAllIds(cursor)
    instance_ids = map(int, instance_ids)
    ids = list(set(instance_ids).difference(set(labeled_ids)))
    return ids

def getLabelIds(cursor, label, experiment_label_id, annotation = False):
    query  = 'SELECT instance_id FROM Labels '
    query += 'WHERE label = "' + label + '" '
    if experiment_label_id is not None:
        query += 'AND experiment_label_id = '
        query += str(experiment_label_id) + ' '
        if annotation:
            query += 'AND annotation '
    query += ';'
    cursor.execute(query)
    return [x[0] for x in cursor.fetchall()]

def getAssociatedLabel(family, cursor, experiment_label_id):
    cursor.execute('SELECT label \
            FROM Labels \
            WHERE experiment_label_id = %s \
            AND family = %s \
            LIMIT 1;',
            (experiment_label_id, str(family)))
    return cursor.fetchone()[0]


def datasetHasFamilies(cursor, project, dataset, experiment_label_id):
    families = getDatasetFamilies(cursor, project, dataset, experiment_label_id)
    if (len(families) == 0):
        return False
    if (len(families) == 1):
        if families[0] == 'other':
            return False
    return True

#####################
### Edit Families ###
#####################

def changeFamilyName(cursor, label, family, new_family_name, experiment_label_id):
    query  = 'UPDATE Labels '
    query += 'SET family = "' + new_family_name + '" '
    query += 'WHERE label = "' + label + '" '
    query += 'AND family = "' + family + '" '
    query += 'AND experiment_label_id = ' + str(experiment_label_id)
    query += ';'
    cursor.execute(query)

def changeFamilyLabel(cursor, label, family, experiment_label_id):
    new_label = labelBooleanToString(not(labelStringToBoolean(label)))
    query  = 'UPDATE Labels '
    query += 'SET label = "' + new_label + '" '
    query += 'WHERE label = "' + label + '" '
    query += 'AND family = "' + family + '" '
    query += 'AND experiment_label_id = ' + str(experiment_label_id)
    query += ';'
    cursor.execute(query)

def mergeFamilies(cursor, label, families, new_family_name, experiment_label_id):
    for family in families:
        changeFamilyName(cursor, label, family, new_family_name, experiment_label_id)
