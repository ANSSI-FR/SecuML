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

import os
import sqlalchemy
import sqlalchemy.orm
import yaml

from SecuML.core.Tools import logging_tools
from SecuML.experiments import db_tables
from SecuML.experiments.Tools.exp_exceptions import SecuMLexpException


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


class SecuMLConfiguration(object):

    def __init__(self, conf_filename):
        conf_filename = self.getConfFilename(conf_filename)
        self.setConf(conf_filename)
        self.setSession()

    def setConf(self, conf_filename):
        with open(conf_filename, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
            self.setDirectories(cfg['input_data_dir'], cfg['output_data_dir'])
            self.setDatabaseURI(cfg['db_uri'])
            self.setLogger(cfg)

    def setSession(self):
        self.engine = self.getEngine()
        db_tables.createTables(self.engine)
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)

    def setLogger(self, cfg):
        logger_level = 'INFO'
        if 'logger_level' in cfg:
            logger_level = cfg['logger_level']
        logger_output = None
        if 'logger_output' in cfg:
            logger_output = cfg['logger_output']
        self.logger = logging_tools.getLogger('SecuML', logger_level, logger_output)

    def setDirectories(self, input_data_dir, output_data_dir):
        self.checkDirectories(input_data_dir, output_data_dir)
        self.input_data_dir = input_data_dir
        self.output_data_dir = output_data_dir

    def checkDirectories(self, input_data_dir, output_data_dir):
        for d in [input_data_dir, output_data_dir]:
            if not os.path.isabs(d):
                raise ConfRelativePaths()

    def getConfFilename(self, conf_filename):
        if conf_filename is not None:
            return conf_filename
        else:
            try:
                return os.environ['SECUMLCONF']
            except KeyError:
                raise SecumlConfMissing()

    def setDatabaseURI(self, db_uri):
        self.checkDatabaseURI(db_uri)
        self.db_uri = db_uri

    def checkDatabaseURI(self, db_uri):
        self.db_type = None
        if db_uri.find('mysql+mysqlconnector://') == 0:
            self.db_type = 'mysql'
        elif db_uri.find('postgresql://') == 0:
            self.db_type = 'postgresql'
        else:
            raise WrongDatabase()

    def getEngine(self):
        if self.db_type == 'mysql':
            engine = sqlalchemy.create_engine(self.db_uri + '?charset=utf8',
                                              echo=False)
        elif self.db_type == 'postgresql':
            engine = sqlalchemy.create_engine(self.db_uri, echo=False)
        else:
            assert(False)
        return engine
