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
from os import listdir
import os.path as path

from SecuML.core.Tools import dir_tools


def getProjectDirectory(secuml_conf, project):
    return path.join(secuml_conf.input_data_dir, project)


def getDatasetDirectory(secuml_conf, project, dataset):
    return path.join(getProjectDirectory(secuml_conf, project),
                     dataset)


def getIdentsFilename(secuml_conf, project, dataset):
    return path.join(getDatasetDirectory(secuml_conf, project, dataset),
                     'idents.csv')


def getGroundTruthFilename(secuml_conf, project, dataset):
    return path.join(getDatasetDirectory(secuml_conf, project, dataset),
                     'annotations',
                     'ground_truth.csv')


def getDatasets(secuml_conf, project):
    project_dir = getProjectDirectory(secuml_conf, project)
    return listdir(project_dir)


def createDataset(secuml_conf, project, dataset):
    dataset_dir = getDatasetDirectory(secuml_conf, project, dataset)
    dir_tools.createDirectory(dataset_dir)
    features_dir = path.join(dataset_dir, 'features')
    dir_tools.createDirectory(features_dir)
    annotations_dir = path.join(dataset_dir, 'annotations')
    dir_tools.createDirectory(annotations_dir)
    return dataset_dir, features_dir, annotations_dir


def getProjectOutputDirectory(secuml_conf, project):
    return path.join(secuml_conf.output_data_dir, project)


def getDatasetOutputDirectory(secuml_conf, project, dataset):
    return path.join(getProjectOutputDirectory(secuml_conf, project), dataset)


def getExperimentOutputDirectory(secuml_conf, project, dataset, experiment_id):
    return path.join(getDatasetOutputDirectory(secuml_conf, project, dataset),
                     str(experiment_id))


def createDatasetOutputDirectory(secuml_conf, project, dataset):
    dir_tools.createDirectory(getDatasetOutputDirectory(secuml_conf,
                                                        project,
                                                        dataset))


def getExperimentConfigurationFilename(secuml_conf, project, dataset,
                                       experiment_id):
    return path.join(getExperimentOutputDirectory(secuml_conf,
                                                  project,
                                                  dataset,
                                                  experiment_id),
                     'conf.json')


def removeProjectOutputDirectory(secuml_conf, project):
    project_dir = getProjectOutputDirectory(secuml_conf, project)
    dir_tools.removeDirectory(project_dir)


def removeDatasetOutputDirectory(secuml_conf, project, dataset):
    dataset_dir = getDatasetOutputDirectory(secuml_conf, project, dataset)
    dir_tools.removeDirectory(dataset_dir)


def annotationsWithFamilies(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        return len(header) == 3
