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

from SecuML.experiments.db_tables import InstancesAlchemy


def getIdent(session, dataset_id, instance_id):
    query = session.query(InstancesAlchemy)
    query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
    query = query.filter(InstancesAlchemy.id == instance_id)
    return query.one().ident


def getRowNumber(session, dataset_id, instance_id):
    query = session.query(InstancesAlchemy)
    query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
    query = query.filter(InstancesAlchemy.id == instance_id)
    return query.one().row_number


def getAllIdents(session, dataset_id):
    query = session.query(InstancesAlchemy)
    query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
    idents = {}
    for r in query.all():
        idents[str(r.id)] = r.ident
    return idents


def getAllUserInstanceIds(session, dataset_id):
    query = session.query(InstancesAlchemy)
    query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
    user_instance_ids = {}
    for r in query.all():
        user_instance_ids[str(r.id)] = r.user_instance_id
    return user_instance_ids
