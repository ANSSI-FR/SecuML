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

import csv
import json

from SecuML.Data import labels_tools
from SecuML.Data import idents_tools

from SecuML.Experiment import experiment_db_tools
from SecuML.Experiment import ExperimentFactory

from SecuML.Tools import dir_tools
from SecuML.Tools import mysql_tools

class Experiment(object):

    def __init__(self, project, dataset, db, cursor,
            experiment_name = None,
            experiment_label = None,
            parent = None):
        self.project = project
        self.dataset = dataset
        self.setDbConnection(db, cursor)
        self.parent = parent
        self.kind = 'Experiment'
        self.experiment_name = experiment_name
        self.experiment_id = None
        self.experiment_label = experiment_label
        self.experiment_label_id = None

    def setDbConnection(self, db, cursor):
        self.db = db
        self.cursor = cursor
        mysql_tools.useDatabase(self.cursor, self.project, self.dataset)

    def getFeaturesFilenames(self):
        return self.features_filenames

    def getFeaturesFilesFullpaths(self):
        features_filenames = self.getFeaturesFilenames()
        features_directory = dir_tools.getDatasetDirectory(
                self.project, self.dataset) + 'features/'
        features_filenames = [features_directory + f for f in features_filenames]
        return features_filenames

    def getFeaturesNames(self):
        features_path = self.getFeaturesFilesFullpaths()
        features_names = []
        for features_file in features_path:
            with open(features_file, 'r') as f_file:
                features_reader = csv.reader(f_file)
                f_features_names = features_reader.next()
                features_names.extend(f_features_names[1:])
        return features_names

    def getFeatures(self, instance_id):
        row_number = idents_tools.getRowNumber(self.cursor, instance_id)
        features_path = self.getFeaturesFilesFullpaths()
        features_names = []
        features_values = []
        for features_file in features_path:
            line = 1
            with open(features_file, 'r') as f_file:
                names_reader = csv.reader(f_file)
                f_features_names = names_reader.next()
                features_names.extend(f_features_names[1:])
                while line < row_number:
                    f_file.next()
                    line = line + 1
                row = f_file.next().rstrip(),
                features_reader = csv.reader(row)
                features_values.extend(features_reader.next()[1:])
        return features_names, features_values

    def setFeaturesFilenames(self, features_filenames):
        self.features_filenames = features_filenames

    def initLabels(self, labels_filename = None, overwrite = True):
        self.generateExperimentName(labels_filename)
        self.createExperiment(overwrite = overwrite)
        if labels_filename is not None:
            self.initFromFile(labels_filename)

    def initFromFile(self, labels_filename):
        filename  = dir_tools.getDatasetDirectory(self.project,
                self.dataset)
        filename += 'labels/' + labels_filename
        if not dir_tools.checkFileExists(filename):
            raise ValueError('The labels file %s does not exist' % filename)
        ## Check whether the file contains families
        families = False
        with open(filename, 'r') as f:
            header = f.readline()
            fields = header.split(',')
            if len(fields) == 3:
                families = True
        query  = 'LOAD DATA LOCAL INFILE \'' + filename + '\' '
        query += 'INTO TABLE ' + 'Labels' + ' '
        query += 'FIELDS TERMINATED BY \',\' '
        query += 'IGNORE 1 LINES '
        if families:
            query += '(instance_id, label, family) '
        else:
            query += '(instance_id, label) '
        query += 'SET experiment_label_id = ' + str(self.experiment_label_id) + ', '
        if not families:
            query += 'family = "other",'
        query += 'iteration = 0, '
        query += 'method = "init", '
        query += 'annotation = "0"'
        query += ';'
        self.cursor.execute(query);
        self.db.commit()

    def generateExperimentName(self, labels_filename):
        if self.experiment_name is None:
            self.experiment_name  = '_'.join([f.split('.')[0] for f in self.features_filenames])
            if labels_filename is not None:
                self.experiment_name +=  '__labelsFile_' + labels_filename.split('.')[0]
            self.experiment_name += self.generateSuffix()

    def createExperiment(self, overwrite = True):
        if self.experiment_label is None:
            self.experiment_label = self.experiment_name
        # Check whether the experiment already exists
        self.cursor.execute('SELECT id, label_id FROM Experiments \
                WHERE name = %s AND kind = %s', (self.experiment_name, self.kind))
        experiment_details = self.cursor.fetchone()
        if experiment_details is not None and not overwrite:
            self.experiment_id, self.experiment_label_id = experiment_details
            return
        else:
            self.removeExperimentDB()
            self.addExperimentDB()
            self.db.commit()

    # If the experiment already exists (same name and same kind),
    # it is removed from the database
    # All the labels corresponding to this experiment are deleted
    def addExperimentDB(self):
        ## Get the experiment_label id
        self.cursor.execute('SELECT id FROM ExperimentsLabels \
                WHERE label = %s', (self.experiment_label,))
        experiment_label_id = self.cursor.fetchone()
        if experiment_label_id is not None:
            self.experiment_label_id = experiment_label_id[0]
        else:
            self.experiment_label_id = experiment_db_tools.addExperimentLabel(
                    self.cursor,
                    self.experiment_label)
        types = ['INT UNSIGNED', 'VARCHAR(200)', 'VARCHAR(1000)',
                'INT UNSIGNED', 'INT UNSIGNED']
        values = [0, self.kind, self.experiment_name,
                self.experiment_label_id, self.parent]
        mysql_tools.insertRowIntoTable(self.cursor, 'Experiments',
                values, types)
        self.experiment_id = mysql_tools.getLastInsertedId(self.cursor)

    ## The labels are deleted only if the experiment has no parent
    def removeExperimentDB(self):
        experiment_id, experiment_label_id = self.isInDB()
        if experiment_id is None:
            return
        self.experiment_id = experiment_id
        self.experiment_label_id = experiment_label_id
        ## Remove children experiments
        children = experiment_db_tools.getChildren(self.cursor, experiment_id)
        for child in children:
            child_exp = ExperimentFactory.getFactory().fromJson(self.project, self.dataset, child,
                    self.db, self.cursor)
            child_exp.removeExperimentDB()
        if self.parent is None:
            labels_tools.removeExperimentLabels(self.cursor,
                    experiment_label_id)
        self.cursor.execute('DELETE FROM Experiments \
                WHERE name = %s \
                AND kind = %s', (self.experiment_name,
                    self.kind, ))
        self.db.commit()
        experiment_dir = dir_tools.getExperimentOutputDirectory(self)
        dir_tools.removeDirectory(experiment_dir)

    def isInDB(self):
        experiment_id, experiment_label_id = None, None
        query  = 'SELECT id, label_id FROM Experiments '
        query += 'WHERE name = "' + self.experiment_name + '" '
        query += 'AND kind = "' + self.kind + '";'
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        if row is not None:
            experiment_id = row[0]
            experiment_label_id = row[1]
        return experiment_id, experiment_label_id

    def generateSuffix(self):
        return ''

    @staticmethod
    def expParamFromJson(experiment, obj):
        experiment.kind                = obj['kind']
        experiment.experiment_name     = obj['experiment_name']
        experiment.experiment_id       = obj['experiment_id']
        experiment.experiment_label    = obj['experiment_label']
        experiment.experiment_label_id = obj['experiment_label_id']
        experiment.features_filenames  = obj['features_filenames']

    @staticmethod
    def fromJson(obj, db, cursor):
        experiment = Experiment(obj['project'], obj['dataset'], db, cursor)
        Experiment.expParamFromJson(experiment, obj)
        return experiment

    def toJson(self):
        conf = {}
        conf['__type__'] = 'Experiment'
        conf['project'] = self.project
        conf['dataset'] = self.dataset
        conf['kind']  = self.kind
        conf['experiment_name']     = self.experiment_name
        conf['experiment_id']       = self.experiment_id
        conf['experiment_label']    = self.experiment_label
        conf['experiment_label_id'] = self.experiment_label_id
        conf['features_filenames']  = self.features_filenames
        return conf

    def export(self):
        experiment_dir = dir_tools.getExperimentOutputDirectory(self)
        dir_tools.createDirectory(experiment_dir)
        conf_filename = experiment_dir + 'conf.json'
        with open(conf_filename, 'w') as f:
            json.dump(self.toJson(), f,
                    indent = 2)

    @staticmethod
    def projectDatasetFeturesParser(parser):
        parser.add_argument('project')
        parser.add_argument('dataset')
        parser.add_argument('--features', '-f',
                dest = 'features_files',
                nargs = '+',
                required = False,
                default = ['features.csv'],
                help = 'CSV files containing the features.')
