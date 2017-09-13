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

import csv
import json

from SecuML import db_tables

from SecuML.Data import labels_tools
from SecuML.Data import idents_tools

from SecuML.Experiment import experiment_db_tools

from SecuML.Tools import dir_tools
from SecuML.Tools import mysql_tools

class Experiment(object):

    def __init__(self, project, dataset, session, experiment_name = None,
                 parent = None):
        self.session         = session
        self.project         = project
        self.dataset         = dataset
        self.dataset_id      = self.setDatasetId()
        self.kind            = 'Experiment'
        self.experiment_name = experiment_name
        self.experiment_id   = None
        self.parent          = parent
        self.oldest_parent   = None

    def setDatasetId(self):
        project_id = db_tables.checkProject(self.session, self.project)
        dataset_id = db_tables.checkDataset(self.session, project_id, self.dataset)
        return dataset_id

    def getOutputDirectory(self):
        output_dir = dir_tools.getDatasetOutputDirectory(self.project,
                                                         self.dataset)
        output_dir += str(self.experiment_id) + '/'
        return output_dir

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
        row_number = idents_tools.getRowNumber(self.session, self.dataset_id, instance_id)
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
        filename  = dir_tools.getDatasetDirectory(self.project, self.dataset)
        filename += 'labels/' + labels_filename
        if not dir_tools.checkFileExists(filename):
            raise ValueError('The labels file %s does not exist.' % filename)
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
        query += 'SET experiment_id = ' + str(self.oldest_parent) + ', '
        query += 'dataset_id =  ' + str(self.dataset_id) + ','
        if not families:
            query += 'family = "other",'
        query += 'iteration = 0, '
        query += 'method = "init", '
        query += 'annotation = "1"'
        query += ';'
        db, cursor = mysql_tools.getSecuMLConnection()
        cursor.execute(query);

        mysql_tools.closeConnection(db, cursor)
        labels_tools.checkLabelsValidity(self.session)

    def generateExperimentName(self, labels_filename):
        if self.experiment_name is None:
            self.experiment_name  = '_'.join([f.split('.')[0] for f in self.features_filenames])
            if labels_filename is not None:
                self.experiment_name +=  '__labelsFile_' + labels_filename.split('.')[0]
            self.experiment_name += self.generateSuffix()

    def createExperiment(self, overwrite = True):
        if self.kind == 'Validation':
            validation = experiment_db_tools.checkValidationExperiment(self.session,
                                                                          self.dataset_id,
                                                                          self.experiment_name)
            if validation is not None:
                self.experiment_id = validation.id
                self.oldest_parent = validation.oldest_parent
                return

        experiment_id, oldest_parent = experiment_db_tools.addExperiment(self.session,
                                                                         self.kind,
                                                                         self.experiment_name,
                                                                         self.dataset_id,
                                                                         self.parent)
        self.experiment_id = experiment_id
        self.oldest_parent = oldest_parent

    def remove(self):
        experiment_db_tools.removeExperiment(self.session, self.experiment_id)
        dir_tools.removeDirectory(self.getOutputDirectory())

    def generateSuffix(self):
        return ''

    @staticmethod
    def expParamFromJson(experiment, obj):
        experiment.kind               = obj['kind']
        experiment.experiment_name    = obj['experiment_name']
        experiment.experiment_id      = obj['experiment_id']
        experiment.features_filenames = obj['features_filenames']
        experiment.parent             = obj['parent']
        experiment.oldest_parent      = obj['oldest_parent']

    @staticmethod
    def fromJson(obj, session):
        experiment = Experiment(obj['project'], obj['dataset'], session)
        Experiment.expParamFromJson(experiment, obj)
        return experiment

    def toJson(self):
        conf = {}
        conf['__type__'] = 'Experiment'
        conf['project'] = self.project
        conf['dataset'] = self.dataset
        conf['kind']  = self.kind
        conf['experiment_name']    = self.experiment_name
        conf['experiment_id']      = self.experiment_id
        conf['features_filenames'] = self.features_filenames
        conf['parent']             = self.parent
        conf['oldest_parent']      = self.oldest_parent
        return conf

    def export(self):
        experiment_dir = self.getOutputDirectory()
        dir_tools.createDirectory(experiment_dir)
        conf_filename = experiment_dir + 'conf.json'
        with open(conf_filename, 'w') as f:
            json.dump(self.toJson(), f, indent = 2)

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
