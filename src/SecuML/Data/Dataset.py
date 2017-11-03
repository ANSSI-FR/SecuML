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

import sys

from SecuML.Tools import dir_tools
from SecuML.Tools import db_tools

from SecuML import db_tables

class Dataset(object):

    def __init__(self, project, dataset, session):
        self.project         = project
        self.dataset         = dataset
        self.session         = session

    def isLoaded(self):
        self.project_id = db_tables.checkProject(self.session, self.project)
        if self.project_id is None:
            return False
        self.dataset_id = db_tables.checkDataset(self.session, self.project_id, self.dataset)
        if self.dataset_id is None:
            return False
        return True

    def load(self):
        self.initDataset()
        ### Load idents and true labels
        self.loadIdents()
        self.loadTrueLabels()

    def remove(self):
        db_tables.removeDataset(self.session, self.project, self.dataset)
        dir_tools.removeDatasetOutputDirectory(self.project, self.dataset)

    #####################
    #####################
    ## Private methods ##
    #####################
    #####################

    def initDataset(self):
        self.createDirectories()
        self.createProjectDataset()

    def createDirectories(self):
        dir_tools.createDirectory(
                dir_tools.getDatasetOutputDirectory(
                    self.project, self.dataset))

    def createProjectDataset(self):
        self.project_id = db_tables.checkProject(self.session, self.project)
        if self.project_id is None:
            self.project_id = db_tables.addProject(self.session, self.project)
        self.dataset_id = db_tables.checkDataset(self.session, self.project_id, self.dataset)
        if self.dataset_id is None:
            self.dataset_id = db_tables.addDataset(self.session, self.project_id, self.dataset)

    def loadIdents(self):
        filename  = dir_tools.getDatasetDirectory(self.project, self.dataset)
        filename += 'idents.csv'
        db, cursor = db_tools.getRawConnection()
        if db_tools.isMysql():
            query  = 'LOAD DATA LOCAL INFILE \'' + filename + '\' '
            query += 'INTO TABLE ' + 'instances' + ' '
            query += 'CHARACTER SET UTF8 '
            query += 'FIELDS TERMINATED BY \',\' '
            query += 'OPTIONALLY ENCLOSED BY \'"\' '
            query += 'IGNORE 1 LINES '
            query += 'SET dataset_id = ' + str(self.dataset_id) + ','
            query += 'row_number = NULL'
            query += ';'
            cursor.execute(query);
            query = 'SET @pos = 0;'
            cursor.execute(query)
            query  = 'UPDATE instances SET row_number = '
            query += '( SELECT @pos := @pos + 1 ) WHERE dataset_id = ' + str(self.dataset_id)
            query += ';'
            cursor.execute(query)
        elif db_tools.isPostgresql():
            query =  'CREATE TEMPORARY TABLE instances_import('
            query += 'user_instance_id integer, '
            query += 'ident varchar(200), '
            query += 'dataset_id integer DEFAULT ' + str(self.dataset_id) + ','
            query += 'row_number serial PRIMARY KEY'
            query += ');'
            cursor.execute(query);
            with open(filename, 'r') as f:
                query  = 'COPY instances_import(user_instance_id,ident) '
                query += 'FROM STDIN '
                query += 'WITH CSV HEADER DELIMITER AS \',\' ;'
                cursor.copy_expert(sql = query, file = f)
            query  = 'INSERT INTO instances(user_instance_id,ident,dataset_id,row_number) '
            query += 'SELECT user_instance_id, ident, dataset_id, row_number '
            query += 'FROM instances_import;'
            cursor.execute(query)
        db_tools.closeRawConnection(db, cursor)

    def loadTrueLabels(self):
        labels_file  = dir_tools.getDatasetDirectory(self.project,
                                                     self.dataset)
        labels_file += 'labels/true_labels.csv'
        # Loads the true labels in the table TrueLabels if the file exists
        # Otherwise the table TrueLabels is not created
        if not dir_tools.checkFileExists(labels_file):
            print >>sys.stderr, 'No ground truth labels for this dataset'
            return

        ## Check whether the file contains families
        families = False
        with open(labels_file, 'r') as f:
            header = f.readline()
            fields = header.split(',')
            if len(fields) == 3:
                families = True
        db, cursor = db_tools.getRawConnection()

        if db_tools.isMysql():
            query =  'CREATE TEMPORARY TABLE true_labels_import('
            query += 'user_instance_id integer PRIMARY KEY, '
            query += 'label varchar(200), '
            query += 'family varchar(200) DEFAULT \'other\', '
            query += 'dataset_id integer DEFAULT ' + str(self.dataset_id) + ', '
            query += 'id integer DEFAULT NULL'
            query += ');'
            cursor.execute(query);

            query  = 'LOAD DATA LOCAL INFILE \'' + labels_file + '\' '
            query += 'INTO TABLE ' + 'true_labels_import' + ' '
            query += 'FIELDS TERMINATED BY \',\' '
            query += 'IGNORE 1 LINES '
            if families:
                query += '(user_instance_id, label, family) '
            else:
                query += '(user_instance_id, label) '
            query += ';'
            cursor.execute(query);

            query  = 'UPDATE true_labels_import t '
            query += 'JOIN instances i '
            query += 'ON i.user_instance_id = t.user_instance_id '
            query += 'AND i.dataset_id = t.dataset_id '
            query += 'SET t.id = i.id;'
            cursor.execute(query)

            query  = 'INSERT INTO true_labels(instance_id, dataset_id, label, family) '
            query += 'SELECT t.id, t.dataset_id, t.label, t.family '
            query += 'FROM true_labels_import AS t;'
            cursor.execute(query)

        elif db_tools.isPostgresql():
            query =  'CREATE TEMPORARY TABLE true_labels_import('
            query += 'user_instance_id integer PRIMARY KEY, '
            query += 'label true_labels_enum, '
            query += 'family varchar(200) DEFAULT \'other\', '
            query += 'dataset_id integer DEFAULT ' + str(self.dataset_id) + ', '
            query += 'id integer DEFAULT NULL'
            query += ');'
            cursor.execute(query);

            with open(labels_file, 'r') as f:
                if families:
                    query  = 'COPY true_labels_import(user_instance_id,label,family) '
                else:
                    query  = 'COPY true_labels_import(user_instance_id,label) '
                query += 'FROM STDIN '
                query += 'WITH CSV HEADER DELIMITER AS \',\' ;'
                cursor.copy_expert(sql = query, file = f)

            query  = 'UPDATE true_labels_import AS t '
            query += 'SET id = i.id '
            query += 'FROM instances AS i '
            query += 'WHERE i.user_instance_id = t.user_instance_id '
            query += 'AND i.dataset_id = t.dataset_id;'
            cursor.execute(query)

            query  = 'INSERT INTO true_labels(instance_id, dataset_id, label, family) '
            query += 'SELECT t.id, t.dataset_id, t.label, t.family '
            query += 'FROM true_labels_import AS t;'
            cursor.execute(query)

        db_tools.closeRawConnection(db, cursor)
