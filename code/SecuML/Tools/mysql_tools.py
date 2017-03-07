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

import math
import mysql.connector
from mysql.connector.constants import ClientFlag
import os
import sys

def getDbConnection(buffered = False):
    home = os.environ['HOME']
    with open(home + '/.my.cnf', 'r') as f:
        header = f.readline()
        host = f.readline().split('=')[1].strip()
        user = f.readline().split('=')[1].strip()
        password = f.readline().split('=')[1].strip()
    db = mysql.connector.connect(host = host, user = user, password = password, unix_socket = '/var/run/mysqld/mysqld.sock', client_flags = [ClientFlag.LOCAL_FILES])
    cursor = db.cursor(buffered = buffered)
    return [db, cursor]

def checkConnection(db, cursor, project, dataset):
    ok = db.is_connected()
    if ok:
        return
    else:
        db.reconnect()
        cursor = db.cursor()
        useDatabase(cursor, project, dataset)

def closeDb(db, cursor):
    cursor.close()
    db.commit()
    db.close()

def databaseExists(cursor, project, dataset):
    try:
        useDatabase(cursor, project, dataset)
        return True
    except:
        return False

def useDatabase(cursor, project, dataset):
    database_name = project + '_' + dataset
    cursor.execute('USE `' + database_name + '`;')

def useDatabaseName(cursor, database_name):
    cursor.execute('USE `' + database_name + '`;')

def dropDatabaseIfExists(cursor, database_name):
    cursor.execute('DROP DATABASE IF EXISTS `' + database_name + '`;')

def createDatabase(cursor, database_name):
    cursor.execute('CREATE DATABASE `' + database_name + '`;')

def removeTableIfExists(cursor, table_name):
    cursor.execute('DROP TABLE IF EXISTS ' + table_name + ';')

def loadCsvFile(cursor, filename, table_name, row_number_field = None):
    query  = 'LOAD DATA LOCAL INFILE %s '
    query += 'INTO TABLE ' + table_name + ' '
    query += 'CHARACTER SET UTF8 '
    query += 'FIELDS TERMINATED BY \',\' '
    query += 'OPTIONALLY ENCLOSED BY \'"\' '
    query += 'IGNORE 1 LINES '
    query += ';'
    cursor.execute(query, (filename,));

def getTables(cursor):
    cursor.execute('SHOW TABLES');
    return [x[0] for x in cursor.fetchall()]

def getCurrentDatabaseName(cursor):
    query = 'SELECT DATABASE();'
    cursor.execute(query)
    return cursor.fetchone()[0]

def tableExist(cursor, database, table):
    if database is None:
        database = getCurrentDatabaseName(cursor)
    cursor.execute("SELECT table_name FROM information_schema.tables \
            WHERE table_schema = %s \
            AND table_name = %s", (database, table))
    answer = cursor.fetchone()
    return answer is not None

def dropTableIfExists(cursor, table_name):
    cursor.execute("DROP TABLE IF EXISTS " + table_name + ";")

def createTableFromFields(cursor, table_name, fields, types, primary_key,
        index = None, auto_increment = False):
    dropTableIfExists(cursor, table_name)
    create_table  = 'CREATE TABLE ' + table_name + ' ('
    for i in range(len(fields)):
        field = fields[i]
        create_table += '`' + str(field) + '` ' + types[i]
        if auto_increment and field == primary_key[0]:
            create_table += " PRIMARY KEY AUTO_INCREMENT"
        if i < len(fields) - 1:
            create_table += ', '
    if index is not None:
        create_table += ", INDEX(" + ",".join(index) + ")"
    if not auto_increment:
        create_table += ", PRIMARY KEY(" + ",".join(primary_key) + ")"
    create_table += ");"
    cursor.execute(create_table)

def insertRowIntoTable(cursor, table_name, features, types):
    command  = 'INSERT INTO ' + table_name + ' VALUES'
    command += '('  
    if features[0] is None:
        command += 'NULL'
    elif types[0].find('BIT') > -1:
        command += '"' + str(math.trunc(float(features[0]))) + '"'
    else:
        command += '"' + str(features[0]) + '"'
    for i in range(1, len(features)):
        if features[i] is None:
            command += ', NULL'
        elif types[i].find('BIT') > -1:
            command += ', b\''
            command += str(math.trunc(float(features[i])))
            command += '\''
        else:
            command += ', "' + str(features[i]) + '"'
    command += ');'
    try:
        cursor.execute(command)
    except mysql.connector.IntegrityError:
        print >>sys.stderr, 'Integrity error'
        print >>sys.stderr, command

def getLastInsertedId(cursor):
    query = 'SELECT LAST_INSERT_ID();'
    cursor.execute(query)
    return cursor.fetchone()[0]
