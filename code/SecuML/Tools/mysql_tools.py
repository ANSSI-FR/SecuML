## SecuML
## Copyright (C) 2016-2017  ANSSI
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

import mysql.connector
from mysql.connector.constants import ClientFlag
import os
import sqlalchemy
import sqlalchemy.orm

def getSecuMLSession():
    home = os.environ['HOME']
    with open(home + '/.my.cnf', 'r') as f:
        f.readline() # skip the header
        host = f.readline().split('=')[1].strip()
        user = f.readline().split('=')[1].strip()
        password = f.readline().split('=')[1].strip()
    connector  = 'mysql+mysqlconnector://' + user + ':'
    connector += password + '@' + host + '/'
    connector += 'SecuML'
    connector += '?charset=utf8'
    engine  = sqlalchemy.create_engine(connector, echo = False)
    Session = sqlalchemy.orm.sessionmaker(bind = engine)
    session = Session()
    return engine, session

def closeSqlAlchemySession(session):
    session.close()
    session.get_bind().dispose()

def getSecuMLConnection(buffered = True):
    home = os.environ['HOME']
    with open(home + '/.my.cnf', 'r') as f:
        f.readline() # skip the header
        host = f.readline().split('=')[1].strip()
        user = f.readline().split('=')[1].strip()
        password = f.readline().split('=')[1].strip()
    db = mysql.connector.connect(host = host, user = user, password = password,
                                 unix_socket = '/var/run/mysqld/mysqld.sock',
                                 client_flags = [ClientFlag.LOCAL_FILES])
    cursor = db.cursor(buffered = buffered)
    cursor.execute('USE SecuML;')
    return [db, cursor]

def closeConnection(db, cursor):
    cursor.close()
    db.commit()
    db.close()
