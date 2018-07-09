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

import csv
import os.path as path

from SecuML.core.Tools import dir_tools

from SecuML.experiments import db_tables
from SecuML.experiments.Tools import db_tools
from SecuML.experiments.Tools import dir_exp_tools


class Dataset(object):

    def __init__(self, project, dataset, session):
        self.project = project
        self.dataset = dataset
        self.session = session

    def isLoaded(self):
        self.project_id = db_tables.checkProject(self.session, self.project)
        if self.project_id is None:
            return False
        self.dataset_id = db_tables.checkDataset(
            self.session, self.project_id, self.dataset)
        if self.dataset_id is None:
            return False
        return True

    def load(self, logger):
        self.initDataset()
        # Load the idents and ground-truth
        self.loadIdents()
        self.loadGroundTruth(logger)

    def remove(self):
        db_tables.removeDataset(self.session, self.project, self.dataset)
        dir_exp_tools.removeDatasetOutputDirectory(self.project, self.dataset)

    def initDataset(self):
        dir_exp_tools.createDatasetOutputDirectory(self.project, self.dataset)
        self.createProjectDataset()

    def createProjectDataset(self):
        self.project_id = db_tables.checkProject(self.session, self.project)
        if self.project_id is None:
            self.project_id = db_tables.addProject(self.session, self.project)
        self.dataset_id = db_tables.checkDataset(
            self.session, self.project_id, self.dataset)
        if self.dataset_id is None:
            self.dataset_id = db_tables.addDataset(
                self.session, self.project_id, self.dataset)

    def loadIdents(self):
        filename = path.join(dir_exp_tools.getDatasetDirectory(
                                       self.project,
                                       self.dataset),
                             'idents.csv')
        db, cursor = db_tools.getRawConnection()
        if db_tools.isMysql():
            query = 'LOAD DATA LOCAL INFILE \'' + filename + '\' '
            query += 'INTO TABLE ' + 'instances' + ' '
            query += 'CHARACTER SET UTF8 '
            query += 'FIELDS TERMINATED BY \',\' '
            query += 'OPTIONALLY ENCLOSED BY \'"\' '
            query += 'IGNORE 1 LINES '
            query += 'SET dataset_id = ' + str(self.dataset_id) + ','
            query += 'row_number = NULL'
            query += ';'
            cursor.execute(query)
            query = 'SET @pos = 0;'
            cursor.execute(query)
            query = 'UPDATE instances SET row_number = '
            query += '( SELECT @pos := @pos + 1 ) WHERE dataset_id = ' + \
                str(self.dataset_id)
            query += ';'
            cursor.execute(query)
        elif db_tools.isPostgresql():
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
            query += 'dataset_id integer DEFAULT ' + str(self.dataset_id) + ','
            query += 'row_number serial PRIMARY KEY'
            query += ');'
            cursor.execute(query)
            with open(filename, 'r') as f:
                if timestamps:
                    query = 'COPY instances_import(user_instance_id,ident,timestamp) '
                else:
                    query = 'COPY instances_import(user_instance_id,ident) '
                query += 'FROM STDIN '
                query += 'WITH CSV HEADER DELIMITER AS \',\' ;'
                cursor.copy_expert(sql=query, file=f)
            query = 'INSERT INTO instances(user_instance_id,ident,timestamp,dataset_id,row_number) '
            query += 'SELECT user_instance_id, ident, timestamp, dataset_id, row_number '
            query += 'FROM instances_import;'
            cursor.execute(query)
        db_tools.closeRawConnection(db, cursor)

    def loadGroundTruth(self, logger):
        annotations_file = path.join(dir_exp_tools.getDatasetDirectory(
                                            self.project,
                                            self.dataset),
                                     'annotations',
                                     'ground_truth.csv')
        if not dir_tools.checkFileExists(annotations_file):
            logger.warning('No ground-truth available for this dataset')
            return

        # Check whether the file contains families
        families = False
        with open(annotations_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            if len(header) == 3:
                families = True
        db, cursor = db_tools.getRawConnection()

        if db_tools.isMysql():
            query = 'CREATE TEMPORARY TABLE ground_truth_import('
            query += 'user_instance_id integer PRIMARY KEY, '
            query += 'label varchar(200), '
            query += 'family varchar(200) DEFAULT \'other\', '
            query += 'dataset_id integer DEFAULT ' + \
                str(self.dataset_id) + ', '
            query += 'id integer DEFAULT NULL'
            query += ');'
            cursor.execute(query)

            query = 'LOAD DATA LOCAL INFILE \'' + annotations_file + '\' '
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

            query = 'INSERT INTO ground_truth(instance_id, dataset_id, label, family) '
            query += 'SELECT t.id, t.dataset_id, t.label, t.family '
            query += 'FROM ground_truth_import AS t;'
            cursor.execute(query)

        elif db_tools.isPostgresql():
            query = 'CREATE TEMPORARY TABLE ground_truth_import('
            query += 'user_instance_id integer PRIMARY KEY, '
            query += 'label ground_truth_enum, '
            query += 'family varchar(200) DEFAULT \'other\', '
            query += 'dataset_id integer DEFAULT ' + \
                str(self.dataset_id) + ', '
            query += 'id integer DEFAULT NULL'
            query += ');'
            cursor.execute(query)

            with open(annotations_file, 'r') as f:
                if families:
                    query = 'COPY ground_truth_import(user_instance_id,label,family) '
                else:
                    query = 'COPY ground_truth_import(user_instance_id,label) '
                query += 'FROM STDIN '
                query += 'WITH CSV HEADER DELIMITER AS \',\' ;'
                cursor.copy_expert(sql=query, file=f)

            query = 'UPDATE ground_truth_import AS t '
            query += 'SET id = i.id '
            query += 'FROM instances AS i '
            query += 'WHERE i.user_instance_id = t.user_instance_id '
            query += 'AND i.dataset_id = t.dataset_id;'
            cursor.execute(query)

            query = 'INSERT INTO ground_truth(instance_id, dataset_id, label, family) '
            query += 'SELECT t.id, t.dataset_id, t.label, t.family '
            query += 'FROM ground_truth_import AS t;'
            cursor.execute(query)

        db_tools.closeRawConnection(db, cursor)
