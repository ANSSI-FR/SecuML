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
import numpy as np


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
        self.__init__(np.hstack((self.ids, ids.get_ids())),
                      idents=np.hstack((self.idents, ids.idents)),
                      timestamps=np.hstack((self.timestamps, ids.timestamps)))

    def get_from_ids(self, instance_ids):
        return Ids(instance_ids,
                   idents=[self.get_ident(i) for i in instance_ids],
                   timestamps=[self.get_timestamp(i) for i in instance_ids])

    def get_from_indices(self, instance_ids, indices):
        if len(instance_ids) == 0:
            return Ids(instance_ids, idents=np.array([]),
                       timestamps=np.array([]))
        else:
            return Ids(instance_ids, idents=self.idents[indices],
                       timestamps=self.timestamps[indices])

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
        return self.ids[self.timestamps > cutoff_time]

    def get_ids_after(self, cutoff_time):
        return self.ids[self.timestamps >= cutoff_time]

    def get_ids_between(self, start, end):
        mask_end = self.timestamps < end
        mask_start = self.timestamps >= start
        mask = np.logical_and(mask_end, mask_start)
        return self.ids[mask]

    @staticmethod
    def deepcopy(ids):
        return Ids(deepcopy(ids.ids), deepcopy(ids.idents),
                   deepcopy(ids.timestamps))

    def _set_idents_timetamps(self, idents, timestamps):
        self.idents = idents
        self.timestamps = timestamps
        num_instances = self.num_instances()
        if self.idents is None:
            self.idents = np.full((num_instances,), None)
        if self.timestamps is None:
            self.timestamps = np.full((num_instances,), None)
