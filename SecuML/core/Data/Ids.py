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


class Ids(object):

    def __init__(self, ids, idents=None):
        self.ids = ids
        self.idents = idents
        self.indexes = {}
        for i in range(len(self.ids)):
            self.indexes[self.ids[i]] = i

    def setIdents(self, idents):
        self.idents = idents

    # The union must be used on instances coming from the same dataset.
    # Otherwise, there may be some collisions on the ids.
    def union(self, ids):
        if ids.numInstances() == 0:
            return
        self.__init__(self.ids + ids.getIds())

    def numInstances(self):
        return len(self.ids)

    def getIndex(self, instance_id):
        return self.indexes[instance_id]

    def getIds(self):
        return self.ids
