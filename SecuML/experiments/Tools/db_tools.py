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

import sqlalchemy
import sqlalchemy.orm
from urllib.parse import urlparse

from SecuML.experiments.config import DB_URI


def isMysql():
    return DB_URI.find('mysql') == 0


def isPostgresql():
    return DB_URI.find('postgresql') == 0


def checkURI():
    if DB_URI is None:
        raise ValueError(
            'The URI of the database (MySQL or PostgreSQL) must be specified '
            'in the SecuML configuration file.')


def getSqlalchemySession():
    checkURI()
    if isMysql():
        engine = sqlalchemy.create_engine(DB_URI + '?charset=utf8', echo=False)
    elif isPostgresql():
        engine = sqlalchemy.create_engine(DB_URI, echo=False)
    else:
        raise ValueError('SecuML supports only PostgreSQL and MySQL.')
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()
    return engine, session


def closeSqlalchemySession(session):
    session.close()
    session.get_bind().dispose()
