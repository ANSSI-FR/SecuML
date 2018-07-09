# SecuML
# Copyright (C) 2016  ANSSI
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

from SecuML.experiments.config import INPUTDATA_DIR, OUTPUTDATA_DIR

from SecuML.core.Tools import dir_tools

from os import listdir
import os.path as path


def getProjectDirectory(project):
    return path.join(INPUTDATA_DIR, project)


def getDatasetDirectory(project, dataset):
    return path.join(getProjectDirectory(project), dataset)


def getDatasets(project):
    project_dir = getProjectDirectory(project)
    return listdir(project_dir)


def createDataset(project, dataset):
    dataset_dir = getDatasetDirectory(project, dataset)
    dir_tools.createDirectory(dataset_dir)
    features_dir = path.join(dataset_dir, 'features')
    dir_tools.createDirectory(features_dir)
    annotations_dir = path.join(dataset_dir, 'annotations')
    dir_tools.createDirectory(annotations_dir)
    return dataset_dir, features_dir, annotations_dir


def getProjectOutputDirectory(project):
    return path.join(OUTPUTDATA_DIR, project)


def getDatasetOutputDirectory(project, dataset):
    return path.join(getProjectOutputDirectory(project), dataset)


def getExperimentOutputDirectory(project, dataset, experiment_id):
    return path.join(getDatasetOutputDirectory(project, dataset),
                     str(experiment_id))


def createDatasetOutputDirectory(project, dataset):
    dir_tools.createDirectory(getDatasetOutputDirectory(project, dataset))


def getExperimentConfigurationFilename(project, dataset, experiment_id):
    return path.join(getExperimentOutputDirectory(project, dataset, experiment_id),
                     'conf.json')


def removeProjectOutputDirectory(project):
    project_dir = getProjectOutputDirectory(project)
    dir_tools.removeDirectory(project_dir)


def removeDatasetOutputDirectory(project, dataset):
    dataset_dir = getDatasetOutputDirectory(project, dataset)
    dir_tools.removeDirectory(dataset_dir)
