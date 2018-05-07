#!/usr/bin/python2
# -*- coding: utf-8 -*-

## SecuML
## Copyright (C) 2017  ANSSI
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

from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as req_file:
    requires = [i.strip() for i in req_file.readlines()]

packages = find_packages()
setup(
        name = 'SecuML',
        version = '0.12',
        description = 'Machine Learning for Computer Security',
        author = ['Anaël Beaugnon', 'Pierre Collet', 'Antoine Husson'],
        author_email = 'anael.beaugnon@ssi.gouv.fr',
        url = 'https://github.com/ANSSI-FR/SecuML',
        licence = 'GPL2+',
        package_dir = {'SecuML': 'SecuML',
            'SecuML_web': 'SecuML_web',
            'CeleryApp': 'CeleryApp'},
        packages = packages,
        include_package_data = True,
        install_requires = requires,
        test_suite = 'test',
        scripts = [
            'SecuML_ILAB',
            'SecuML_DIADEM',
            'SecuML_clustering',
            'SecuML_descriptive_statistics',
            'SecuML_feature_selection',
            'SecuML_projection',
            'SecuML_rare_category_detection',
            'SecuML_remove_project_dataset',
            'SecuML_server'
            ]
)
