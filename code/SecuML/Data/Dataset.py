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

import sys

from SecuML.Data import labels_tools
from SecuML.Experiment.Experiment import Experiment
from SecuML.Experiment import experiment_db_tools
from SecuML.Tools import dir_tools
from SecuML.Tools import mysql_tools

class Dataset(object):

    def __init__(self, project, dataset, db, cursor):
        self.project         = project
        self.dataset         = dataset
        self.db, self.cursor = db, cursor

    def load(self):
        self.initDataset()
        ## Create tables
        labels_tools.createLabelsTable(self.cursor)
        experiment_db_tools.createExperimentsTable(self.cursor)
        experiment_db_tools.createExperimentsLabelsTable(self.cursor)
        experiment_db_tools.createPredictedLabelsAnalysisTable(self.cursor)
        ## Load idents and true labels
        self.loadIdents()
        self.loadTrueLabels()

    #####################
    #####################
    ## Private methods ##
    #####################
    #####################

    def initDataset(self):
        self.createDirectories()
        self.createDatabase()

    def createDirectories(self):
        dir_tools.createDirectory(
                dir_tools.getDatasetOutputDirectory(
                    self.project, self.dataset))

    def createDatabase(self):
        database_name = self.project + '_' + self.dataset
        mysql_tools.dropDatabaseIfExists(self.cursor, database_name)
        mysql_tools.createDatabase(self.cursor, database_name)
        mysql_tools.useDatabase(self.cursor, self.project, self.dataset)

    def loadIdents(self):
        row_number_field = 'row_number'
        idents_file = dir_tools.getDatasetDirectory(
                self.project, self.dataset) + 'idents.csv'
        fields = ['instance_id', 'ident', row_number_field]
        types  = ['INT', 'VARCHAR(200) CHARACTER SET utf8', 'INT NOT NULL AUTO_INCREMENT']
        mysql_tools.createTableFromFields(self.cursor, 'Idents',
                fields, types,
                [row_number_field, 'instance_id'])
        mysql_tools.loadCsvFile(self.cursor, idents_file, 'Idents', row_number_field)

    def loadTrueLabels(self):
        labels_file  = dir_tools.getDatasetDirectory(self.project,
                self.dataset)
        labels_file += 'labels/true_labels.csv'
        # Loads the true labels in the table TrueLabels if the file exists
        # Otherwise the table TrueLabels is not created
        if not dir_tools.checkFileExists(labels_file):
            print >>sys.stderr, 'No ground truth labels for this dataset'
            return
        exp = Experiment(self.project, self.dataset,
                self.db, self.cursor,
                experiment_name = 'true_labels')
        exp.initLabels('true_labels.csv')
