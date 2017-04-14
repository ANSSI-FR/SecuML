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

from SecuML.config import INPUTDATA_DIR, OUTPUTDATA_DIR

import os
import shutil

def getProjectDirectory(project):
    project_dir  = INPUTDATA_DIR + '/'
    project_dir += project + '/'
    return project_dir

def getDatasets(project):
    project_dir = getProjectDirectory(project)
    return os.listdir(project_dir)

def createDataset(project, dataset):
    dataset_dir = getDatasetDirectory(project, dataset)
    createDirectory(dataset_dir)
    features_dir = dataset_dir + 'features/'
    createDirectory(features_dir)
    labels_dir = dataset_dir + 'labels/'
    createDirectory(labels_dir)
    return dataset_dir, features_dir, labels_dir

def getDatasetDirectory(project, dataset):
    dataset_dir  = getProjectDirectory(project)
    dataset_dir += dataset + '/'
    return dataset_dir

def getProjectOutputDirectory(project):
    project_dir  = OUTPUTDATA_DIR
    project_dir += '/' + project + '/'
    return project_dir

def getDatasetOutputDirectory(project, dataset):
    dataset_dir  = getProjectOutputDirectory(project)
    dataset_dir += dataset + '/'
    return dataset_dir

def getExperimentConfigurationFilename(project, dataset, experiment_id):
    experiment_dir  = getDatasetOutputDirectory(project, dataset)
    experiment_dir += str(experiment_id) + '/'
    conf_filename = experiment_dir + 'conf.json'
    return conf_filename

def removeProjectOutputDirectory(project):
    project_dir = getProjectOutputDirectory(project)
    removeDirectory(project_dir)

def removeDatasetOutputDirectory(project, dataset):
    dataset_dir = getDatasetOutputDirectory(project, dataset)
    removeDirectory(dataset_dir)

def getExperimentOutputDirectory(experiment):
    experiment_dir  = getDatasetOutputDirectory(
            experiment.project,
            experiment.dataset)
    experiment_dir += str(experiment.experiment_id) + '/'
    return experiment_dir

## If the input directory does not exist
## it is created
def checkDirectoryExists(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)
        return False
    return True

def checkFileExists(filename):
    return os.path.isfile(filename)

## If the directory exists, it is deleted
## A new directory is created
def createDirectory(directory):
    removeDirectory(directory)
    os.makedirs(directory)

## If the directory exists, it is deleted
def removeDirectory(directory):
    if os.path.isdir(directory):
        shutil.rmtree(directory)

def countLines(filename):
    with open(filename, 'r') as f:
        for i, l in enumerate(f):
            pass
    return i + 1
