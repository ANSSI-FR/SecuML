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

import os
from sqlalchemy.orm import sessionmaker
import yaml

from secuml.core.tools.logging import close_logger, get_logger
from secuml.exp.tools.db_tables import Base
from secuml.exp.tools.db_tables import call_specific_db_func
from secuml.exp.tools.exp_exceptions import SecuMLexpException


class SecumlConfMissing(SecuMLexpException):

    def __str__(self):
        return('No configuration file provided. \n'
               'The environment variable SECUMLCONF must be set '
               'to the path of the configuration file.')


class ConfRelativePaths(SecuMLexpException):

    def __str__(self):
        return('The configuration file must contain absolute paths '
               'for input_data_dir and output_data_dir.')


class WrongDatabase(SecuMLexpException):

    def __str__(self):
        return('The URI of the database (MySQL or PostgreSQL) must be '
               'specified in the secuml configuration file.\n'
               'MySQL databases: '
               '"mysql+mysqlconnector://<user>:<password>@<host>/<db_name>"\n'
               'postgresql databases: '
               'postgresql://<user>:<password>@<host>/<db_name>"')


class SecuMLConf(object):

    def __init__(self, conf_filename):
        conf_filename = self.get_conf_filename(conf_filename)
        self._set_conf(conf_filename)
        self._set_session()

    def _set_conf(self, conf_filename):
        with open(conf_filename, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
            self.set_directories(cfg['input_data_dir'], cfg['output_data_dir'])
            self.set_db_uri(cfg['db_uri'])
            self._set_logger(cfg)
            self._set_host_port(cfg)

    def _set_session(self):
        self.engine = self.get_engine()
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _set_logger(self, cfg):
        logger_level = 'INFO'
        if 'logger_level' in cfg:
            logger_level = cfg['logger_level']
        logger_output = None
        if 'logger_output' in cfg:
            logger_output = cfg['logger_output']
        self.logger, self.log_handler = get_logger('SecuML', logger_level,
                                                   logger_output)

    def _set_host_port(self, cfg):
        self.host = 'localhost'
        if 'host' in cfg:
            self.host = cfg['host']
        self.port = 8080
        if 'port' in cfg:
            self.port = int(cfg['port'])

    def close_log_handler(self):
        close_logger(self.logger, self.log_handler)

    def set_directories(self, input_data_dir, output_data_dir):
        self._check_directories(input_data_dir, output_data_dir)
        self.input_data_dir = input_data_dir
        self.output_data_dir = output_data_dir
        self.secuml_dir = os.path.abspath(os.path.join(
                                                os.path.dirname(__file__),
                                                '..', '..'))

    def _check_directories(self, input_data_dir, output_data_dir):
        for d in [input_data_dir, output_data_dir]:
            if not os.path.isabs(d):
                raise ConfRelativePaths()

    def get_conf_filename(self, conf_filename):
        if conf_filename is not None:
            return conf_filename
        else:
            try:
                return os.environ['SECUMLCONF']
            except KeyError:
                raise SecumlConfMissing()

    def set_db_uri(self, db_uri):
        self.check_db_uri(db_uri)
        self.db_uri = db_uri

    def check_db_uri(self, db_uri):
        self.db_type = None
        if db_uri.find('mysql+mysqlconnector://') == 0:
            self.db_type = 'mysql'
        elif db_uri.find('postgresql://') == 0:
            self.db_type = 'postgresql'
        else:
            raise WrongDatabase()

    def get_engine(self):
        return call_specific_db_func(self.db_type, 'get_engine',
                                     (self.db_uri,))
