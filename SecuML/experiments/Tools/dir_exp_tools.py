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

from os import listdir
import os.path as path
from urllib.parse import urlparse

from SecuML.core.Tools import dir_tools

from SecuML.experiments.config import INPUTDATA_DIR
from SecuML.experiments.config import OUTPUTDATA_DIR
from SecuML.experiments.config import SECUML_DIR


class MissingWebLibraries(Exception):

    def __init__(self):
        self.message  = 'Some JS or CSS libraries are missing in SecuML/web/static/lib/. '
        self.message += 'You can download them with the script download_libraries. \n'

    def __str__(self):
        return self.message


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
    return path.join(getExperimentOutputDirectory(project,
                                                  dataset,
                                                  experiment_id),
                     'conf.json')


def removeProjectOutputDirectory(project):
    project_dir = getProjectOutputDirectory(project)
    dir_tools.removeDirectory(project_dir)


def removeDatasetOutputDirectory(project, dataset):
    dataset_dir = getDatasetOutputDirectory(project, dataset)
    dir_tools.removeDirectory(dataset_dir)


def getWebUrls():
    urls = {}
    urls['js'] = ['https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.17/d3.min.js',
                  'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.0/jquery.min.js',
                  'https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
                  'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.2.2/Chart.min.js',
                  'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.0/js/bootstrap.min.js']
    urls['css'] = ['http://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
                   'https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.css']
    return urls

def checkWebLibraries():
    lib_dir = path.join(SECUML_DIR, 'web', 'static', 'lib')
    web_urls = getWebUrls()
    for k in ['js', 'css']:
        directory = path.join(lib_dir, k)
        libs = [path.basename(urlparse(u).path) for u in web_urls[k]]
        for lib in libs:
            if not dir_tools.checkFileExists(path.join(directory, lib)):
                raise MissingWebLibraries()
