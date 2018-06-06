# SecuML
# Copyright (C) 2016-2017  ANSSI
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

import os
import yaml


class SecumlConfMissing(Exception):
    def __str__(self):
        return 'The environment variable SECUMLCONF must be set to the path of the configuration file.'


try:
    config_path = os.environ['SECUMLCONF']
except KeyError as e:
    raise SecumlConfMissing()

with open(config_path, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
    INPUTDATA_DIR = cfg['input_data_dir']
    OUTPUTDATA_DIR = cfg['output_data_dir']
    DB_URI = cfg['db_uri']
