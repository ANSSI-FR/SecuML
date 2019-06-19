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

import hashlib

from secuml.exp.tools.db_tables import InstancesAlchemy


def get_dataset_ids_timestamps(session, dataset_id):
    query = session.query(InstancesAlchemy)
    query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
    query = query.order_by(InstancesAlchemy.id)
    return zip(*[(r.id, r.timestamp) for r in query.all()])


def compute_hash(filename, kind='md5'):
    BLOCKSIZE = 65536
    if kind == 'md5':
        hasher = hashlib.md5()
    elif kind == 'sha1':
        hasher = hashlib.sha1()
    else:
        assert(False)
    with open(filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()
