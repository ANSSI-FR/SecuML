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

import abc
import csv
import json
import numpy as np
import os.path as path
import pandas as pd

from SecuML.core.Tools import colors_tools
from SecuML.core.Tools import dir_tools

from . import experiment_db_tools
from . import db_tables
from .Data import idents_tools
from .Data.Dataset import Dataset
from .Tools import dir_exp_tools
from .Tools import mysql_specific
from .Tools import postgresql_specific
from .Tools.exp_exceptions import SecuMLexpException


class FeaturesFileNotFound(SecuMLexpException):

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return('The features file %s does not exist.'
                % self.filename)


class Experiment(object):

    def __init__(self, secuml_conf, session=None):
        self.secuml_conf = secuml_conf
        if session is None:
            self.session = secuml_conf.Session()
        else:
            self.session = session
        self.logger = self.secuml_conf.logger
        self.experiment_id = None

    def initExperiment(self, project, dataset, experiment_name=None,
                       parent=None, create=True):
        if create:
            self._loadDataset(project, dataset)
        self._initExperiment(project, dataset, experiment_name, parent)
        if create:
            self.addToDb()

    def rollbackSession(self):
        self.session.rollback()
        self.session.close()
        if self.experiment_id is not None:
            dir_tools.removeDirectory(self.getOutputDirectory())

    def close(self):
        self.closeSession()
        print(colors_tools.displayInGreen(
                '\nExperiment %d has been successfully completed. \n'
                'See http://localhost:5000/SecuML/%d/ '
                'to display the results. \n' %
                (self.experiment_id, self.experiment_id)))


    def closeSession(self):
        self.session.commit()
        self.session.close()

    def export(self):
        experiment_dir = self.getOutputDirectory()
        dir_tools.createDirectory(experiment_dir)
        conf_filename = path.join(experiment_dir, 'conf.json')
        with open(conf_filename, 'w') as f:
            json.dump(self.toJson(), f, indent=2)

    def setConf(self, conf, features_filename, annotations_filename=None,
                annotations_id=None):
        self.conf = conf
        self._initAnnotations(annotations_filename, annotations_id)
        self._setFeaturesFilename(features_filename)
        self._generateExperimentName()
        self._checkConf()

    def _checkConf(self):
        # Check features file
        features_filename = self.getFeaturesFullpath()
        if not path.isfile(features_filename):
            raise FeaturesFileNotFound(features_filename)

    def getOutputDirectory(self):
        return dir_exp_tools.getExperimentOutputDirectory(self.secuml_conf,
                                                          self.project,
                                                          self.dataset,
                                                          self.experiment_id)

    def getFeaturesFullpath(self):
        dataset_dir = dir_exp_tools.getDatasetDirectory(self.secuml_conf,
                                                        self.project,
                                                        self.dataset)
        features_directory = path.join(dataset_dir, 'features')
        full_path = path.join(features_directory,
                              self.features_filename)
        return full_path

    def getFeaturesNamesDescriptions(self):
        features_file = self.getFeaturesFullpath()
        features_names = []
        features_descriptions = []
        basename, ext = path.splitext(features_file)
        features_description_file = basename + '_description.csv'
        if dir_tools.checkFileExists(features_description_file):
            with open(features_description_file, 'r') as f:
                df = pd.read_csv(f, header=0, index_col=0)
                features_names.extend(df['name'])
                features_descriptions.extend(df['description'])
        else:
            with open(features_file, 'r') as f_file:
                features_reader = csv.reader(f_file)
                f_features_names = next(features_reader)
                features_names.extend(f_features_names[1:])
                features_descriptions.extend(f_features_names[1:])
        return features_names, features_descriptions

    def getFeatures(self, instance_id):
        features_names, _ = self.getFeaturesNamesDescriptions()
        row_number = idents_tools.getRowNumber(
            self.session, self.dataset_id, instance_id)
        features_file = self.getFeaturesFullpath()
        features_values = []
        line = 1
        with open(features_file, 'r') as f_file:
            next(f_file)  # skip header
            while line < row_number:
                next(f_file)
                line = line + 1
            row = next(f_file).rstrip(),
            features_reader = csv.reader(row)
            features_values.extend(next(features_reader)[1:])
        return features_names, features_values

    def getAllFeatures(self):
        csv_file = self.getFeaturesFullpath()
        try:
            with open(csv_file, 'r') as f:
                f.readline()
                current_features = list(list(rec) for rec in csv.reader(
                                    f,
                                    quoting=csv.QUOTE_NONNUMERIC))
                features = [l[1:] for l in current_features]
        except FileNotFoundError:
            raise FeaturesFileNotFound(csv_file)
        features = np.array(features)
        return features

    def remove(self):
        experiment_db_tools.removeExperiment(self.session, self.experiment_id)
        dir_tools.removeDirectory(self.getOutputDirectory())

    def generateSuffix(self):
        return ''

    @staticmethod
    def expParamFromJson(experiment, obj, conf):
        experiment.project = obj['project']
        experiment.dataset = obj['dataset']
        experiment.dataset_id = obj['dataset_id']
        experiment.conf = conf
        experiment.kind = obj['kind']
        experiment.experiment_name = obj['experiment_name']
        experiment.experiment_id = obj['experiment_id']
        experiment.features_filename = obj['features_filename']
        experiment.parent = obj['parent']
        experiment.oldest_parent = obj['oldest_parent']
        experiment.annotations_id = obj['annotations_id']
        experiment.annotations_type = obj['annotations_type']

    def toJson(self):
        conf = {}
        conf['__type__'] = 'Experiment'
        conf['project'] = self.project
        conf['dataset'] = self.dataset
        conf['dataset_id'] = self.dataset_id
        conf['kind'] = self.kind
        conf['experiment_name'] = self.experiment_name
        conf['experiment_id'] = self.experiment_id
        conf['features_filename'] = self.features_filename
        conf['parent'] = self.parent
        conf['oldest_parent'] = self.oldest_parent
        conf['annotations_id'] = self.annotations_id
        conf['annotations_type'] = self.annotations_type
        return conf

    @staticmethod
    def projectDatasetFeturesParser(parser):
        parser.add_argument('project')
        parser.add_argument('dataset')
        parser.add_argument('--features', '-f',
                            dest='features_file',
                            required=False,
                            default='features.csv',
                            help='CSV file containing the features. '
                                 'Default: features.csv')
        parser.add_argument('--exp-name', type=str,
                            required=False,
                            default=None,
                            help='Name of the experiment. '
                                 'If not provided, a default name is '
                                 'automatically generated from the input '
                                 'parameters.')
        parser.add_argument('--secuml-conf', type=str,
                            required=False,
                            default=None,
                            help='YAML file containing the configuration. '
                                 'If conf is not set, the configuration is '
                                 'read from the file stored in the environment '
                                 'variable SECUMLCONF.')

    @abc.abstractmethod
    def setExperimentFromArgs(self, args):
        return

    def _initExperiment(self, project, dataset, experiment_name, parent):
        self.project = project
        self.dataset = dataset
        self.dataset_id = self._setDatasetId()
        self.kind = self.getKind()
        self.experiment_name = experiment_name
        self.experiment_id = None
        self.parent = parent
        self.oldest_parent = None
        self.annotations_id = None
        self.annotations_type = None

    def _loadDataset(self, project, dataset):
        dataset = Dataset(self.secuml_conf, self.session, project, dataset)
        dataset.load(self.logger)

    def _setDatasetId(self):
        project_id = db_tables.checkProject(self.session, self.project)
        dataset_id = db_tables.checkDataset(self.session,
                                            project_id,
                                            self.dataset)
        return dataset_id

    def _generateExperimentName(self):
        if self.experiment_name is None:
            basename, ext = path.splitext(self.features_filename)
            self.experiment_name = basename
            self.experiment_name += self.generateSuffix()
            experiment_db_tools.updateExperimentName(
                self.session, self.experiment_id, self.experiment_name)

    def _setFeaturesFilename(self, features_filename):
        self.features_filename = features_filename

    def _initAnnotations(self, annotations_filename, annotations_id):
        if annotations_id is not None:
            self._setAnnotationsId(annotations_id)
        else:
            self._setAnnotationsFilename(annotations_filename)

    def _setAnnotationsId(self, annotations_id):
        query = self.session.query(db_tables.ExperimentAnnotationsAlchemy)
        query = query.filter(
            db_tables.ExperimentAnnotationsAlchemy.annotations_id == annotations_id)
        exp_annotations = query.one()
        self.annotations_id = exp_annotations.annotations_id
        self.annotations_type = exp_annotations.annotations_type

    def _setAnnotationsFilename(self, annotations_filename):
        if annotations_filename is None:
            annotations_type = 'none'
        elif annotations_filename == 'ground_truth.csv':
            annotations_type = 'ground_truth'
        else:
            annotations_type = 'partial_annotations'

        exp_annotations = db_tables.ExperimentAnnotationsAlchemy(
            experiment_id=self.experiment_id,
            annotations_type=annotations_type)
        self.session.add(exp_annotations)
        self.session.flush()
        self.annotations_id = exp_annotations.annotations_id
        self.annotations_type = annotations_type

        if annotations_type == 'partial_annotations':
            filename = path.join(dir_exp_tools.getDatasetDirectory(
                                                self.secuml_conf,
                                                self.project,
                                                self.dataset),
                                 'annotations',
                                 annotations_filename)
            if not dir_tools.checkFileExists(filename):
                raise ValueError(
                    'The annotation file %s does not exist.' % filename)
            families = dir_exp_tools.annotationsWithFamilies(filename)
            conn = self.session.connection().connection
            cursor = conn.cursor()
            if self.secuml_conf.db_type == 'mysql':
                mysql_specific.loadPartialAnnotations(cursor,
                                                      filename,
                                                      families,
                                                      self.annotations_id,
                                                      self.dataset_id)
            if self.secuml_conf.db_type == 'postgresql':
                postgresql_specific.loadPartialAnnotations(cursor,
                                                           filename,
                                                           families,
                                                           self.annotations_id,
                                                           self.dataset_id)
            self.session.flush()

    def addToDb(self):
        experiment_id, oldest_parent = experiment_db_tools.addExperiment(
                            self.session,
                            self.kind,
                            self.experiment_name,
                            self.dataset_id,
                            self.parent)
        self.experiment_id = experiment_id
        self.oldest_parent = oldest_parent
