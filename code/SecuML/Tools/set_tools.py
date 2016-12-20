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

def loadSet(file_name, integers):
    s = set([])
    with open(file_name, 'r') as f:
        for line in f:
            s.add(line.rstrip('\n'))
    if integers:
        s = set(map(int, s))
    return s

def printSet(s, file_name):
    with open(file_name, 'w') as f:
        for elem in s:
            print >>f, elem
