#!/usr/bin/python3

# SecuML
# Copyright (C) 2016-2019  ANSSI
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

import argparse
import os.path as path
import yaml


def gen_yml_conf(db_type, dir_):
    if db_type == 'mysql':
        db_uri = 'mysql+mysqlconnector://travis@localhost/secuml'
    elif db_type == 'psql':
        db_uri = 'postgresql://localhost/secuml'
    else:
        raise ValueError('db_uri must be mysql or psql.')
    travis_conf = {'input_data_dir': path.join(dir_, 'input_data'),
                   'output_data_dir': path.join(dir_, 'output_data'),
                   'db_uri': db_uri,
                   'logger_level': 'ERROR'}
    with open(path.join('conf', 'travis_%s.yml' % db_type), 'w') as f:
        yaml.dump(travis_conf, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('travis_build_dir')
    args = parser.parse_args()
    dir_ = args.travis_build_dir
    for db_type in ['mysql', 'psql']:
        gen_yml_conf(db_type, dir_)
