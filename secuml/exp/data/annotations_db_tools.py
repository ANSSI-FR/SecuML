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

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from secuml.core.data.labels_tools import label_bool_to_str
from secuml.exp.conf.annotations import AnnotationsTypes
from secuml.exp.tools.db_tables import AnnotationsAlchemy
from secuml.exp.tools.db_tables import DatasetsAlchemy
from secuml.exp.tools.db_tables import InstancesAlchemy


def get_annotation(session, annotations_type, annotations_id, dataset_id,
                   instance_id):
    if annotations_type == AnnotationsTypes.partial:
        return get_instance_partial_annotation(session, annotations_id,
                                               instance_id)
    elif annotations_type == AnnotationsTypes.ground_truth:
        return get_instance_ground_truth(session, dataset_id, instance_id)
    elif annotations_type == AnnotationsTypes.ground_truth_if_exists:
        if has_ground_truth(session, dataset_id):
            return get_instance_ground_truth(session, dataset_id, instance_id)
    else:
        return None


def get_instance_partial_annotation_row(session, annotations_id, instance_id):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    query = query.filter(AnnotationsAlchemy.instance_id == int(instance_id))
    try:
        return query.one()
    except NoResultFound:
        return None


def get_instance_partial_annotation(session, annotations_id, instance_id):
    row = get_instance_partial_annotation_row(session, annotations_id,
                                              instance_id)
    if row is None:
        return None
    else:
        return row.label, row.family


def get_instance_ground_truth(session, dataset_id, instance_id):
    query = session.query(InstancesAlchemy)
    query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
    query = query.filter(InstancesAlchemy.id == int(instance_id))
    try:
        row = query.one()
        return row.label, row.family
    except NoResultFound:
        return None


def get_annotated_instances(session, annotations_id):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    return [(r.instance_id, r.label, r.family) for r in query.all()]


def get_dataset_families(session, annotations_id):
    query = session.query(AnnotationsAlchemy.family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    query = query.distinct(AnnotationsAlchemy.family)
    families = [r.family for r in query.all()]
    return families


def has_ground_truth(session, dataset_id):
    query = session.query(DatasetsAlchemy)
    query = query.filter(DatasetsAlchemy.id == dataset_id)
    return query.one().ground_truth


def get_labels_families(session, annotations_type, annotations_id, dataset_id,
                        instance_ids=None, iter_max=None):
    if annotations_type == AnnotationsTypes.ground_truth:
        query = get_labels_families_gt(session, dataset_id, instance_ids)
    elif annotations_type == AnnotationsTypes.ground_truth_if_exists:
        if has_ground_truth(session, dataset_id):
            query = get_labels_families_gt(session, dataset_id, instance_ids)
        else:
            return {}
    elif annotations_type == AnnotationsTypes.partial:
        query = get_labels_families_partial(session, annotations_id,
                                            instance_ids, iter_max)
    else:
        assert(False)
    labels = {}
    for r in query.all():
        label = label_bool_to_str(r.label)
        if label not in list(labels.keys()):
            labels[label] = {}
        labels[label][r.family] = 0
    return labels


def get_labels_families_gt(session, dataset_id, instance_ids):
    query = session.query(InstancesAlchemy)
    query = query.distinct(InstancesAlchemy.label, InstancesAlchemy.family)
    query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
    if instance_ids is not None:
        query = query.filter(InstancesAlchemy.id.in_(instance_ids))
    return query


def get_labels_families_partial(session, annotations_id, instance_ids,
                                iter_max):
    query = session.query(AnnotationsAlchemy)
    query = query.distinct(AnnotationsAlchemy.label, AnnotationsAlchemy.family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    if iter_max is not None:
        query = query.filter(AnnotationsAlchemy.iteration <= iter_max)
    if instance_ids is not None:
        query = query.filter(AnnotationsAlchemy.instance_id.in_(instance_ids))
    return query


def get_label_family_ids(session, annotations_type, annotations_id, dataset_id,
                         label, family=None, iter_max=None, instance_ids=None):
    if annotations_type == AnnotationsTypes.ground_truth:
        return get_label_family_ids_gt(session, dataset_id, label, family,
                                       instance_ids)
    elif annotations_type == AnnotationsTypes.partial:
        return get_label_family_ids_partial(session, annotations_id, label,
                                            family, iter_max, instance_ids)
    else:
        assert(False)


def get_label_family_ids_partial(session, annotations_id, label, family,
                                 iter_max, instance_ids):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    query = query.filter(AnnotationsAlchemy.label == label)
    if family is not None:
        query = query.filter(AnnotationsAlchemy.family == family)
    if iter_max is not None:
        query = query.filter(AnnotationsAlchemy.iteration <= iter_max)
    if instance_ids is not None:
        query = query.filter(AnnotationsAlchemy.instance_id.in_(instance_ids))
    return [r.instance_id for r in query.all()]


def get_label_family_ids_gt(session, dataset_id, label, family, instance_ids):
    query = session.query(InstancesAlchemy)
    query = query.filter(InstancesAlchemy.dataset_id == dataset_id)
    query = query.filter(InstancesAlchemy.label == label)
    if family is not None:
        query = query.filter(InstancesAlchemy.family == family)
    if instance_ids is not None:
        query = query.filter(InstancesAlchemy.id.in_(instance_ids))
    return [r.instance_id for r in query.all()]


def get_unlabeled_ids(session, annotations_type, annotations_id, instance_ids):
    if instance_ids is None:
        assert(False)
    if annotations_type == AnnotationsTypes.ground_truth:
        return []
    annotated_instances = map(lambda x: x[0],
                              get_annotated_instances(session, annotations_id))
    return list(set(instance_ids) - set(annotated_instances))


def get_families_counts(session, annotations_id, iter_max=None, label=None):
    query = session.query(AnnotationsAlchemy.family,
                          func.count(AnnotationsAlchemy.family))
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    if iter_max is not None:
        query = query.filter(AnnotationsAlchemy.iteration <= iter_max)
    if label is not None:
        query = query.filter(AnnotationsAlchemy.label == label)
    query = query.group_by(AnnotationsAlchemy.family)
    family_counts = {}
    for r in query.all():
        family_counts[r[0]] = r[1]
    return family_counts


def add_annotation(session, annotations_id, instance_id, label, family,
                   iter_num, method):
    annotation = AnnotationsAlchemy(annotations_id=annotations_id,
                                    # MySQL does not support numpy int64 type
                                    instance_id=int(instance_id),
                                    label=label,
                                    # MySQL does not support numpy str_ type
                                    family=str(family),
                                    iteration=iter_num,
                                    method=method)
    session.add(annotation)
    session.flush()


def update_annotation(session, annotations_id, instance_id, label, family,
                      iter_num, method):
    row = get_instance_partial_annotation_row(session, annotations_id,
                                              instance_id)
    if row is None:
        add_annotation(session, annotations_id, instance_id, label, family,
                       iter_num, method)
    else:
        row.label = label
        row.family = family
        row.iteration = iter_num
        row.method = method
        session.flush()


def remove_annotation(session, annotations_id, instance_id):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.instance_id == instance_id)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    query.delete()


def change_family_name(session, annotations_id, label, family, new_family):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.label == label)
    query = query.filter(AnnotationsAlchemy.family == family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    instances = query.all()
    for instance in instances:
        instance.family = new_family
    session.flush()


def change_family_label(session, annotations_id, label, family):
    query = session.query(AnnotationsAlchemy)
    query = query.filter(AnnotationsAlchemy.label == label)
    query = query.filter(AnnotationsAlchemy.family == family)
    query = query.filter(AnnotationsAlchemy.annotations_id == annotations_id)
    instances = query.all()
    new_label = not label
    for instance in instances:
        instance.label = new_label
    session.flush()


def merge_families(session, annotations_id, label, families, new_family):
    for family in families:
        change_family_name(session, annotations_id, label, family, new_family)
