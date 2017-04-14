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

import json

## The file f contains several JSON
## The function returns a string containing
## only one JSON
## If there is no JSON left to read,
## the function returns ''
def extractJson(f):
    l = f.readline()
    if l == '':
        return ''
    assert l == '{\n'
    s = l
    while True:
        l = f.readline()
        if l == '}\n':
            s += '}'
            break
        s += l
    return s

def getJsonObject(json_filename):
    with open(json_filename, 'r') as f:
        json_object = json.load(f)
    return json_object
