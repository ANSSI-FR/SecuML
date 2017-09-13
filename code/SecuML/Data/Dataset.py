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

from SecuML.Data import labels_tools
from SecuML.Experiment.TrueLabelsExperiment import TrueLabelsExperiment
from SecuML.Tools import dir_tools
from SecuML.Tools import mysql_tools

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
        try:
            self.initDataset()
            ### Load idents and true labels
            self.loadIdents()
            self.loadTrueLabels()
        except labels_tools.InvalidLabels as e:
            self.remove()
            print 'The dataset has not been loaded.'
            raise e

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
        query  = 'LOAD DATA LOCAL INFILE \'' + filename + '\' '
        query += 'INTO TABLE ' + 'Instances' + ' '
        query += 'CHARACTER SET UTF8 '
        query += 'FIELDS TERMINATED BY \',\' '
        query += 'OPTIONALLY ENCLOSED BY \'"\' '
        query += 'IGNORE 1 LINES '
        query += 'SET dataset_id = ' + str(self.dataset_id) + ','
        query += 'row_number = NULL'
        query += ';'
        db, cursor = mysql_tools.getSecuMLConnection()
        cursor.execute(query);
        query = 'SET @pos = 0;'
        cursor.execute(query)
        query  = 'UPDATE Instances SET row_number = '
        query += '( SELECT @pos := @pos + 1 ) WHERE dataset_id = ' + str(self.dataset_id)
        query += ';'
        cursor.execute(query)
        mysql_tools.closeConnection(db, cursor)

    def loadTrueLabels(self):
        labels_file  = dir_tools.getDatasetDirectory(self.project,
                                                     self.dataset)
        labels_file += 'labels/true_labels.csv'
        # Loads the true labels in the table TrueLabels if the file exists
        # Otherwise the table TrueLabels is not created
        if not dir_tools.checkFileExists(labels_file):
            print >>sys.stderr, 'No ground truth labels for this dataset'
            return
        exp = TrueLabelsExperiment(self.project, self.dataset, self.session)
        exp.initLabels('true_labels.csv')
