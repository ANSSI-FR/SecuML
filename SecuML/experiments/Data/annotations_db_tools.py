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

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from SecuML.core.Data import labels_tools

from SecuML.experiments.db_tables import ExperimentsAlchemy
from SecuML.experiments.db_tables import ExperimentAnnotationsAlchemy
from SecuML.experiments.db_tables import AnnotationsAlchemy
from SecuML.experiments.db_tables import GroundTruthAlchemy


def getAnnotationsId(session, experiment_id):
    # Get oldest parent
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    res = query.one()
    oldest_parent = res.oldest_parent
    dataset_id = res.dataset_id
    query = session.query(ExperimentAnnotationsAlchemy)
    query = query.filter(
        ExperimentAnnotationsAlchemy.experiment_id == oldest_parent)
    res = query.one()
    annotations_type = res.annotations_type
    annotations_id = res.annotations_id
    return annotations_id, annotations_type, dataset_id


def getAnnotationRow(session, experiment_id, instance_id):
    annotations_id, annotations_type, dataset_id = getAnnotationsId(
        session, experiment_id)
    if annotations_type == 'partial_annotations':
        query = session.query(AnnotationsAlchemy)
        query = query.filter(
            AnnotationsAlchemy.instance_id == int(instance_id))
        query = query.filter(
            AnnotationsAlchemy.annotations_id == annotations_id)
        try:
            row = query.one()
            return row
        except NoResultFound:
            return None
    elif annotations_type == 'ground_truth':
        query = session.query(GroundTruthAlchemy)
        query = query.filter(GroundTruthAlchemy.dataset_id == dataset_id)
        query = query.filter(
            GroundTruthAlchemy.instance_id == int(instance_id))
        try:
            row = query.one()
            row.method = 'ground_truth'
            return row
        except NoResultFound:
            return None


def getAnnotation(session, experiment_id, instance_id):
    row = getAnnotationRow(session, experiment_id, instance_id)
    if row is None:
        return None
    else:
        return row.label, row.family


def getAnnotationDetails(session, experiment_id, instance_id):
    row = getAnnotationRow(session, experiment_id, instance_id)
    if row is None:
        return None
    else:
        return row.label, row.family, row.method


def getDatasetId(session, experiment_id):
    query = session.query(ExperimentsAlchemy)
    query = query.filter(ExperimentsAlchemy.id == experiment_id)
    res = query.one()
    return res.dataset_id


def getGroundTruth(session, experiment_id):
    dataset_id = getDatasetId(session, experiment_id)
    query = session.query(GroundTruthAlchemy)
    query = query.filter(GroundTruthAlchemy.dataset_id == dataset_id)
    query = query.order_by(GroundTruthAlchemy.instance_id)
    res = query.all()
    labels = [labels_tools.labelStringToBoolean(r.label) for r in res]
    families = [r.family for r in res]
    return labels, families


def datasetHasFamilies(session, experiment_id):
    families = getDatasetFamilies(session, experiment_id)
    if (len(families) == 0):
        return False
    if (len(families) == 1):
        if families[0] == 'other':
            return False
    return True


def getLabelsFamilies(session, experiment_id, instance_ids=None,
                      iteration_max=None):
    annotations_id, annotations_type, _ = getAnnotationsId(
        session, experiment_id)
    if annotations_type == 'none':
        return {}
    if annotations_type == 'ground_truth':
        assert(False)
    query = session.query(AnnotationsAlchemy)
    query = query.distinct(AnnotationsAlchemy.label, AnnotationsAlchemy.family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    if iteration_max is not None:
        query = query.filter(AnnotationsAlchemy.iteration <= iteration_max)
    if instance_ids is not None:
        query = query.filter(AnnotationsAlchemy.instance_id.in_(instance_ids))
    labels = {}
    for r in query.all():
        if r.label not in list(labels.keys()):
            labels[r.label] = {}
        labels[r.label][r.family] = 0
    return labels


def getFamiliesCounts(session, experiment_id, iteration_max=None, label=None):
    annotations_id, _, _ = getAnnotationsId(session, experiment_id)
    query = session.query(AnnotationsAlchemy.family,
                          func.count(AnnotationsAlchemy.family))
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    if iteration_max is not None:
        query = query.filter(AnnotationsAlchemy.iteration <= iteration_max)
    if label is not None:
        query = query.filter(AnnotationsAlchemy.label == label)
    query = query.group_by(AnnotationsAlchemy.family)
    family_counts = {}
    for r in query.all():
        family_counts[r[0]] = r[1]
    return family_counts


def getLabelFamilyIds(session, experiment_id, label, family=None,
                      iteration_max=None, instance_ids=None):
    annotations_id, _, _ = getAnnotationsId(session, experiment_id)
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    query = query.filter(AnnotationsAlchemy.label == label)
    if family is not None:
        query = query.filter(AnnotationsAlchemy.family == family)
    if iteration_max is not None:
        query = query.filter(AnnotationsAlchemy.iteration <= iteration_max)
    if instance_ids is not None:
        query = query.filter(AnnotationsAlchemy.instance_id.in_(instance_ids))
    instance_ids = [r.instance_id for r in query.all()]
    return instance_ids


def getLabelIds(session, experiment_id, label):
    annotations_id, annotations_type, dataset_id = getAnnotationsId(
        session, experiment_id)
    if annotations_type == 'none':
        return []
    if annotations_type == 'ground_truth':
        query = session.query(GroundTruthAlchemy)
        query = query.filter(GroundTruthAlchemy.label == label)
        query = query.filter(GroundTruthAlchemy.dataset_id == dataset_id)
    elif annotations_type == 'partial_annotations':
        query = session.query(AnnotationsAlchemy)
        query = query.filter(AnnotationsAlchemy.label == label)
        query = query.filter(
            AnnotationsAlchemy.annotations_id == annotations_id)
    instance_ids = [r.instance_id for r in query.all()]
    return instance_ids


def getUnlabeledIds(session, experiment_id, instance_ids=None,
                    iteration_max=None):
    annotations_id, _, _ = getAnnotationsId(session, experiment_id)
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    if iteration_max is not None:
        query = query.filter(AnnotationsAlchemy.iteration <= iteration_max)
    if instance_ids is not None:
        query = query.filter(AnnotationsAlchemy.instance_id.in_(instance_ids))
    instance_ids = [r.instance_id for r in query.all()]
    return instance_ids

#########################
## Update Annotations ###
#########################


def addAnnotation(session, experiment_id, instance_id, label, family,
                  iteration_number, method):
    annotations_id, _, _ = getAnnotationsId(session, experiment_id)
    label = AnnotationsAlchemy(annotations_id=annotations_id,
                               # MySQL does not support numpy types (int64)
                               instance_id=int(instance_id),
                               label=label,
                               family=family,
                               iteration=iteration_number,
                               method=method)
    session.add(label)
    session.flush()


def removeAnnotation(session, experiment_id, instance_id):
    annotations_id, _, _ = getAnnotationsId(session, experiment_id)
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.instance_id == instance_id)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    try:
        label = query.one()
        session.delete(label)
        session.flush()
    except NoResultFound:
        return None

####################
## Edit Families ###
####################


def changeFamilyName(session, experiment_id, label, family, new_family_name):
    annotations_id, _, _ = getAnnotationsId(session, experiment_id)
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.label == label)
    query = query.filter(AnnotationsAlchemy.family == family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    instances = query.all()
    for instance in instances:
        instance.family = new_family_name
    session.flush()


def changeFamilyLabel(session, experiment_id, label, family):
    annotations_id, _, _ = getAnnotationsId(session, experiment_id)
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.label == label)
    query = query.filter(AnnotationsAlchemy.family == family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    instances = query.all()
    new_label = labels_tools.labelBooleanToString(
        not(labels_tools.labelStringToBoolean(label)))
    for instance in instances:
        instance.label = new_label
    session.flush()


def mergeFamilies(session, experiment_id, label, families, new_family_name):
    for family in families:
        changeFamilyName(session, experiment_id, label,
                         family, new_family_name)


def getDatasetFamilies(session, experiment_id):
    annotations_id, _, _ = getAnnotationsId(session, experiment_id)
    query = session.query(AnnotationsAlchemy.family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    query = query.distinct(AnnotationsAlchemy.family)
    families = [r.family for r in query.all()]
    return families
