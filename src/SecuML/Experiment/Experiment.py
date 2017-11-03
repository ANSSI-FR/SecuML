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

import abc
import csv
import json

from SecuML import db_tables

from SecuML.Data import idents_tools
from SecuML.Data.Dataset import Dataset

from SecuML.Tools import dir_tools
from SecuML.Tools import db_tools

import experiment_db_tools

class Experiment(object):

    def __init__(self, project, dataset, session, experiment_name = None,
                 labels_id = None, parent = None):
        if session is None:
            self.session = self.initDatabase(project, dataset)
        else:
            self.session = session
        self.initExperiment(project, dataset, experiment_name, parent, labels_id)

    def initExperiment(self, project, dataset, experiment_name, parent, labels_id):
        self.project         = project
        self.dataset         = dataset
        self.dataset_id      = self.setDatasetId()
        self.kind            = 'Experiment'
        self.experiment_name = experiment_name
        self.experiment_id   = None
        self.parent          = parent
        self.oldest_parent   = None
        self.labels_id       = labels_id
        self.labels_type     = None

    def initDatabase(self, project, dataset):
        engine, session = db_tools.getSqlalchemySession()
        db_tables.createTables(engine)
        load_dataset = Dataset(project, dataset, session)
        if not load_dataset.isLoaded():
            load_dataset.load()
        return session

    def closeSession(self):
        db_tools.closeSqlalchemySession(self.session)

    def setDatasetId(self):
        project_id = db_tables.checkProject(self.session, self.project)
        dataset_id = db_tables.checkDataset(self.session, project_id, self.dataset)
        return dataset_id

    def getOutputDirectory(self):
        output_dir = dir_tools.getDatasetOutputDirectory(self.project,
                                                         self.dataset)
        output_dir += str(self.experiment_id) + '/'
        return output_dir

    def getFeaturesFilesFullpaths(self):
        features_filenames = self.features_filenames
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
        self.initFromFile(labels_filename)

    def initFromFile(self, labels_filename):
        if labels_filename  is None:
            labels_type = 'none'
        elif labels_filename == 'true_labels.csv':
            labels_type = 'true_labels'
        else:
            labels_type = 'partial_labels'

        exp_labels = db_tables.ExperimentsLabelsAlchemy(
                experiment_id = self.experiment_id,
                labels_type = labels_type)
        self.session.add(exp_labels)
        self.session.commit()
        self.labels_id = exp_labels.labels_id
        self.labels_type = labels_type

        if labels_type == 'partial_labels':
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
            db, cursor = db_tools.getRawConnection()

            if db_tools.isMysql():
                query =  'CREATE TEMPORARY TABLE labels_import('
                query += 'instance_id integer, '
                query += 'labels_id integer DEFAULT ' + str(self.labels_id) + ', '
                query += 'user_instance_id integer, '
                query += 'label varchar(200), '
                query += 'family varchar(200) DEFAULT \'other\', '
                query += 'iteration integer DEFAULT 0, '
                query += 'method varchar(200) DEFAULT \'init\', '
                query += 'annotation boolean DEFAULT True'
                query += ');'
                cursor.execute(query);

                query  = 'LOAD DATA LOCAL INFILE \'' + filename + '\' '
                query += 'INTO TABLE ' + 'labels_import' + ' '
                query += 'FIELDS TERMINATED BY \',\' '
                query += 'IGNORE 1 LINES '
                if families:
                    query += '(user_instance_id, label, family) '
                else:
                    query += '(user_instance_id, label) '
                query += ';'
                cursor.execute(query);

                query  = 'UPDATE labels_import l '
                query += 'JOIN instances i '
                query += 'ON i.user_instance_id = l.user_instance_id '
                query += 'AND i.dataset_id = ' + str(self.dataset_id) + ' '
                query += 'SET l.instance_id = i.id;'
                cursor.execute(query)

                query  = 'INSERT INTO labels(instance_id,labels_id,label,family,iteration,method,annotation) '
                query += 'SELECT instance_id,labels_id,label,family,iteration,method,annotation '
                query += 'FROM labels_import;'
                cursor.execute(query)

            elif db_tools.isPostgresql():
                query =  'CREATE TEMPORARY TABLE labels_import('
                query += 'instance_id integer, '
                query += 'labels_id integer DEFAULT ' + str(self.labels_id) + ', '
                query += 'user_instance_id integer, '
                query += 'label labels_enum, '
                query += 'family varchar(200) DEFAULT \'other\', '
                query += 'iteration integer DEFAULT 0, '
                query += 'method varchar(200) DEFAULT \'init\', '
                query += 'annotation boolean DEFAULT True'
                query += ');'
                cursor.execute(query);

                with open(filename, 'r') as f:
                    if families:
                        query  = 'COPY labels_import(user_instance_id,label,family) '
                    else:
                        query  = 'COPY labels_import(user_instance_id,label) '
                    query += 'FROM STDIN '
                    query += 'WITH CSV HEADER DELIMITER AS \',\' ;'
                    cursor.copy_expert(sql = query, file = f)

                query  = 'UPDATE labels_import AS l '
                query += 'SET instance_id = i.id '
                query += 'FROM instances AS i '
                query += 'WHERE i.user_instance_id = l.user_instance_id '
                query += 'AND i.dataset_id = ' + str(self.dataset_id) + ';'
                cursor.execute(query)

                query  = 'INSERT INTO labels(instance_id,labels_id,label,family,iteration,method,annotation) '
                query += 'SELECT instance_id,labels_id,label,family,iteration,method,annotation '
                query += 'FROM labels_import;'
                cursor.execute(query)

            db_tools.closeRawConnection(db, cursor)
            self.session.commit()

    def generateExperimentName(self, labels_filename):
        if self.experiment_name is None:
            self.experiment_name  = '_'.join([f.split('.')[0] for f in self.features_filenames])
            if labels_filename is not None:
                self.experiment_name +=  '__labelsFile_' + labels_filename.split('.')[0]
            self.experiment_name += self.generateSuffix()

    def createExperiment(self, overwrite = True):
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
        experiment.labels_id          = obj['labels_id']

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
        conf['labels_id']          = self.labels_id
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
        help_exp_name  = 'Name of the experiment. '
        help_exp_name += 'If not provided, a default name is automatically generated from the input parameters.'
        parser.add_argument('--exp-name', type = str,
                            required = False,
                            default = None,
                            help = help_exp_name)

    @abc.abstractmethod
    def setExperimentFromArgs(self, args):
        return
