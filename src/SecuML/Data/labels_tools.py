## SecuML
## Copyright (C) 2016-2017  ANSSI
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

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from SecuML.db_tables import ExperimentsLabelsAlchemy
from SecuML.db_tables import LabelsAlchemy
from SecuML.db_tables import TrueLabelsAlchemy

MALICIOUS = 'malicious'
BENIGN    = 'benign'

def labelBooleanToString(label):
    if label:
        return MALICIOUS
    else:
        return BENIGN

def labelStringToBoolean(label):
    return label == MALICIOUS

def getLabel(session, instance_id, experiment_id):
    query = session.query(ExperimentsLabelsAlchemy)
    query = query.filter(ExperimentsLabelsAlchemy.experiment_id == experiment_id)
    res = query.one()
    labels_type = res.labels_type
    labels_id   = res.labels_id
    dataset_id  = res.experiment.dataset_id

    if labels_type == 'partial_labels':
        query = session.query(LabelsAlchemy)
        query = query.filter(LabelsAlchemy.instance_id == instance_id)
        query = query.filter(LabelsAlchemy.labels_id == labels_id)
        try:
            res = query.one()
            return res.label, res.family
        except NoResultFound:
            return None
    elif labels_type == 'true_labels':
        query = session.query(TrueLabelsAlchemy)
        query = query.filter(TrueLabelsAlchemy.dataset_id == dataset_id)
        query = query.filter(TrueLabelsAlchemy.instance_id == instance_id)
        res = query.one()
        return res.label, res.family
    else:
        return None

def getLabelDetails(experiment, instance_id):
    if experiment.labels_type == 'partial_labels':
        query = experiment.session.query(LabelsAlchemy)
        query = query.filter(LabelsAlchemy.instance_id == int(instance_id))
        query = query.filter(LabelsAlchemy.labels_id == int(experiment.labels_id))
        try:
            res = query.one()
            return res.label, res.family, res.method, res.annotation
        except NoResultFound:
            return None
    if experiment.labels_type == 'true_labels':
        query = experiment.session.query(TrueLabelsAlchemy)
        query = query.filter(TrueLabelsAlchemy.instance_id == int(instance_id))
        try:
            res = query.one()
            return res.label, res.family, 'true_labels', True
        except NoResultFound:
            return None
    return None

def getTrueLabelsFamilies(experiment):
    query = experiment.session.query(TrueLabelsAlchemy)
    query = query.filter(TrueLabelsAlchemy.dataset_id == experiment.dataset_id)
    query = query.order_by(TrueLabelsAlchemy.instance_id)
    res = query.all()
    labels = [labelStringToBoolean(r.label) for r in res]
    families = [r.family for r in res]
    return labels, families

def getExperimentLabelsFamilies(session, labels_id):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.labels_id == labels_id)
    query = query.order_by(LabelsAlchemy.instance_id)
    res = query.all()
    labels = [labelStringToBoolean(r.label) for r in res]
    families = [r.family for r in res]
    return labels, families

def getDatasetFamilies(session, labels_id):
    query = session.query(LabelsAlchemy.family)
    query = query.filter(LabelsAlchemy.labels_id == labels_id)
    query = query.distinct(LabelsAlchemy.family)
    families = [r.family for r in query.all()]
    return families

def datasetHasFamilies(session, labels_id):
    families = getDatasetFamilies(session, labels_id)
    if (len(families) == 0):
        return False
    if (len(families) == 1):
        if families[0] == 'other':
            return False
    return True

def getLabelsFamilies(session, labels_id, instance_ids = None,
                      iteration_max = None):
    query = session.query(LabelsAlchemy)
    query = query.distinct(LabelsAlchemy.label, LabelsAlchemy.family)
    query = query.filter(LabelsAlchemy.labels_id == labels_id)
    if iteration_max is not None:
        query = query.filter(LabelsAlchemy.iteration <= iteration_max)
    if instance_ids is not None:
        query = query.filter(LabelsAlchemy.instance_id.in_(instance_ids))
    labels = {}
    for r in query.all():
        if r.label not in labels.keys():
            labels[r.label] = {}
        labels[r.label][r.family] = 0
    return labels

def getFamiliesCounts(session, labels_id, iteration_max = None, label = None):
    query = session.query(LabelsAlchemy.family, func.count(LabelsAlchemy.family))
    query = query.filter(LabelsAlchemy.labels_id == labels_id)
    if iteration_max is not None:
        query = query.filter(LabelsAlchemy.iteration <= iteration_max)
    if label is not None:
        query = query.filter(LabelsAlchemy.label == label)
    query = query.group_by(LabelsAlchemy.family)
    family_counts = {}
    for r in query.all():
        family_counts[r[0]] = r[1]
    return family_counts

def getLabelFamilyIds(session, labels_id, label, family = None,
                      iteration_max = None, instance_ids = None):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.labels_id == labels_id)
    query = query.filter(LabelsAlchemy.label == label)
    if family is not None:
        query = query.filter(LabelsAlchemy.family == family)
    if iteration_max is not None:
        query = query.filter(LabelsAlchemy.iteration <= iteration_max)
    if instance_ids is not None:
        query = query.filter(LabelsAlchemy.instance_id.in_(instance_ids))
    instance_ids = [r.instance_id for r in query.all()]
    return instance_ids

def getLabelIds(experiment, label, annotation = False):
    if experiment.labels_type == 'none':
        return []
    if experiment.labels_type == 'true_labels':
        query = experiment.session.query(TrueLabelsAlchemy)
        query = query.filter(TrueLabelsAlchemy.label == label)
        query = query.filter(TrueLabelsAlchemy.dataset_id == experiment.dataset_id)
    elif experiment.labels_type == 'partial_labels':
        query = experiment.session.query(LabelsAlchemy)
        query = query.filter(LabelsAlchemy.label == label)
        query = query.filter(LabelsAlchemy.labels_id == experiment.labels_id)
        if annotation:
            query= query.filter(LabelsAlchemy.annotation)
    instance_ids = [r.instance_id for r in query.all()]
    return instance_ids

def getAssociatedLabel(session, family, labels_id):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.labels_id == labels_id)
    query = query.filter(LabelsAlchemy.family == str(family)) # MySQL does not support unicode_ type
    query = query.limit(1)
    res = query.one()
    return res.label

def getUnlabeledIds(session, labels_id, instance_ids = None,
                    iteration_max = None):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.labels_id == labels_id)
    if iteration_max is not None:
        query = query.filter(LabelsAlchemy.iteration <= iteration_max)
    if instance_ids is not None:
        query = query.filter(LabelsAlchemy.instance_id.in_(instance_ids))
    instance_ids = [r.instance_id for r in query.all()]
    return instance_ids

#####################
### Update Labels ###
#####################

def addLabel(session, labels_id, instance_id, label, family,
             iteration_number, method, annotation):
    label = LabelsAlchemy(labels_id = labels_id,
                          instance_id = int(instance_id), # MySQL does not support numpy types (int64)
                          label = label,
                          family = family,
                          iteration = iteration_number,
                          method = method,
                          annotation = annotation)
    session.add(label)
    session.commit()

def removeLabel(session, labels_id, instance_id):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.instance_id == instance_id)
    query = query.filter(LabelsAlchemy.labels_id == labels_id)
    try:
        label = query.one()
        session.delete(label)
        session.commit()
    except NoResultFound:
        return None

#####################
### Edit Families ###
#####################

def changeFamilyName(session, label, family, new_family_name, labels_id):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.label == label)
    query = query.filter(LabelsAlchemy.family == family)
    query = query.filter(LabelsAlchemy.labels_id == labels_id)
    instances = query.all()
    for instance in instances:
        instance.family = new_family_name
    session.commit()

def changeFamilyLabel(session, label, family, labels_id):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.label == label)
    query = query.filter(LabelsAlchemy.family == family)
    query = query.filter(LabelsAlchemy.labels_id == labels_id)
    instances = query.all()
    new_label = labelBooleanToString(not(labelStringToBoolean(label)))
    for instance in instances:
        instance.label = new_label
    session.commit()

def mergeFamilies(session, label, families, new_family_name, labels_id):
    for family in families:
        changeFamilyName(session, label, family, new_family_name, labels_id)
