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

def getInstanceIdMax(cursor):
    cursor.execute('SELECT MAX(Idents.instance_id) FROM Idents')
    id_max = cursor.fetchone()[0]
    return id_max

def getAllIds(cursor):
    query  = 'SELECT Idents.instance_id '
    query += 'FROM Idents;'
    cursor.execute(query)
    ids = [int(x[0]) for x in cursor.fetchall()]
    return ids

def getIdent(cursor, instance_id):
    cursor.execute('SELECT Idents.ident FROM Idents \
            WHERE Idents.instance_id = %s', (instance_id,))
    ident = cursor.fetchone()[0]
    return ident

def getRowNumber(cursor, instance_id):
    cursor.execute('SELECT Idents.row_number FROM Idents \
            WHERE Idents.instance_id = %s', (instance_id,))
    row_number = cursor.fetchone()[0]
    return row_number

def getAllIdents(cursor):
    query  = 'SELECT Idents.ident '
    query += 'FROM Idents;'
    cursor.execute(query)
    return [x[0] for x in cursor.fetchall()]

def getIdents(cursor, ids):
    if len(ids) == 0:
        return []
    query  = 'SELECT Idents.ident '
    query += 'FROM Idents '
    query += 'WHERE Idents.instance_id IN ('
    query += ','.join(map(str, ids)) + ');'
    cursor.execute(query)
    return [x[0] for x in cursor.fetchall()]

def getIds(cursor, idents):
    if len(idents) == 0:
        return []
    query  = 'SELECT Idents.instance_id '
    query += 'FROM Idents '
    query += 'WHERE Idents.ident IN ('
    query += ','.join(['"' + x + '"' for x in idents]) + ');'
    cursor.execute(query)
    return [x[0] for x in cursor.fetchall()]

def getNumInstances(cursor):
    query  = 'SELECT COUNT(*) '
    query += 'FROM Idents;'
    cursor.execute(query)
    return int(cursor.fetchone()[0])
