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

from copy import deepcopy


class Ids(object):

    def __init__(self, ids, idents=None, timestamps=None):
        self.ids = ids
        self._set_idents_timetamps(idents, timestamps)
        self.indexes = {}
        for i in range(len(self.ids)):
            self.indexes[self.ids[i]] = i

    # The union must be used on instances coming from the same dataset.
    # Otherwise, there may be some collisions on the ids.
    def union(self, ids):
        if ids.num_instances() == 0:
            return
        self.__init__(self.ids + ids.get_ids(),
                      idents=self.idents + ids.idents,
                      timestamps=self.timestamps + ids.timestamps)

    def get_from_ids(self, instance_ids):
        return Ids(instance_ids,
                   idents=[self.get_ident(i) for i in instance_ids],
                   timestamps=[self.get_timestamp(i) for i in instance_ids])

    def num_instances(self):
        return len(self.ids)

    def get_index(self, instance_id):
        return self.indexes[instance_id]

    def get_ids(self):
        return self.ids

    def get_ident(self, instance_id):
        return self.idents[self.get_index(instance_id)]

    def get_timestamp(self, instance_id):
        return self.timestamps[self.get_index(instance_id)]

    def get_ids_before(self, cutoff_time):
        return [self.ids[i] for i, t in enumerate(self.timestamps)
                if t < cutoff_time]

    def get_ids_after(self, cutoff_time):
        return [self.ids[i] for i, t in enumerate(self.timestamps)
                if t >= cutoff_time]

    def get_ids_between(self, start, end):
        return [self.ids[i] for i, t in enumerate(self.timestamps)
                if t < end and t >= start]

    @staticmethod
    def deepcopy(ids):
        return Ids(deepcopy(ids.ids), deepcopy(ids.idents),
                   deepcopy(ids.timestamps))

    def _set_idents_timetamps(self, idents, timestamps):
        self.idents = idents
        self.timestamps = timestamps
        if self.idents is None:
            self.idents = [None for _ in range(self.num_instances())]
        if self.timestamps is None:
            self.timestamps = [None for _ in range(self.num_instances())]
