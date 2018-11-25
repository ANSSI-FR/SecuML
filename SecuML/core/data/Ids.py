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

    def __init__(self, ids, idents=None, timestamps=None):
        self.ids = ids
        self.setIdentsTimestamps(idents, timestamps)
        self.indexes = {}
        for i in range(len(self.ids)):
            self.indexes[self.ids[i]] = i

    def setIdentsTimestamps(self, idents, timestamps):
        self.idents = idents
        self.timestamps = timestamps
        if self.idents is None:
            self.idents = [None for _ in range(self.numInstances())]
        if self.timestamps is None:
            self.timestamps = [None for _ in range(self.numInstances())]

    # The union must be used on instances coming from the same dataset.
    # Otherwise, there may be some collisions on the ids.
    def union(self, ids):
        if ids.numInstances() == 0:
            return
        self.__init__(self.ids + ids.getIds(),
                      idents=self.idents + ids.idents,
                      timestamps=self.timestamps + ids.timestamps)

    def numInstances(self):
        return len(self.ids)

    def getIndex(self, instance_id):
        return self.indexes[instance_id]

    def getIds(self):
        return self.ids

    def getIdent(self, instance_id):
        index = self.getIndex(instance_id)
        return self.idents[index]

    def getTimestamp(self, instance_id):
        index = self.getIndex(instance_id)
        return self.timestamps[index]

    def getIdsBefore(self, cutoff_time):
        select = [self.ids[i] for i, t in enumerate(self.timestamps) if t < cutoff_time]
        return select

    def getIdsAfter(self, cutoff_time):
        select = [self.ids[i] for i, t in enumerate(self.timestamps) if t >= cutoff_time]
        return select

    def getIdsBetween(self, start, end):
        select = [self.ids[i] for i, t in enumerate(self.timestamps) if t < end and t >= start]
        return select

    def getIdentsTimestampsFromIds(self, instance_ids):
        idents = [self.getIdent(i) for i in instance_ids]
        timestamps = [self.getTimestamp(i) for i in instance_ids]
        return idents, timestamps
