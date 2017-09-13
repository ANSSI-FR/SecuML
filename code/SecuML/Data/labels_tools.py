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

from SecuML.db_tables import LabelsAlchemy

class InvalidLabels(Exception):

    def __init__(self, invalid_values):
        self.message  = 'The labels must be "malicious" or "benign". '
        self.message += 'Invalid values encountered: '
        self.message += ','.join(invalid_values) + '.'

    def __str__(self):
        return self.message

def labelBooleanToString(label):
    if label:
        return 'malicious'
    else:
        return 'benign'

def labelStringToBoolean(label):
    return label == 'malicious'

def checkLabelsValidity(session):
    query = session.query(LabelsAlchemy).distinct(LabelsAlchemy.label)
    labels_values = set([r.label for r in query.all()])
    other_values = list(labels_values.difference(set(['malicious', 'benign'])))
    if len(other_values) != 0:
        raise InvalidLabels(other_values)

def getLabel(session, instance_id, experiment_id):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.instance_id == instance_id)
    query = query.filter(LabelsAlchemy.experiment_id == experiment_id)
    try:
        res = query.one()
        return res.label, res.family
    except NoResultFound:
        return None

def getLabelDetails(session, instance_id, experiment_id):
    query = session.query(LabelsAlchemy).filter(LabelsAlchemy.instance_id == int(instance_id),
                                                LabelsAlchemy.experiment_id == int(experiment_id))
    try:
        res = query.one()
        return res.label, res.family, res.method, res.annotation
    except NoResultFound:
        return None

def getExperimentLabelsFamilies(session, experiment_id):
    query = session.query(LabelsAlchemy).filter(LabelsAlchemy.experiment_id == experiment_id).order_by(LabelsAlchemy.instance_id)
    res = query.all()
    labels = [labelStringToBoolean(r.label) for r in res]
    families = [r.family for r in res]
    return labels, families

def getDatasetFamilies(session, experiment_id):
    query = session.query(LabelsAlchemy).distinct(LabelsAlchemy.family).filter(LabelsAlchemy.experiment_id == experiment_id)
    families = [r.family for r in query.all()]
    return families

def datasetHasFamilies(session, experiment_id):
    families = getDatasetFamilies(session, experiment_id)
    if (len(families) == 0):
        return False
    if (len(families) == 1):
        if families[0] == 'other':
            return False
    return True

def getLabelsFamilies(session, experiment_id, instance_ids = None,
                      iteration_max = None):
    query = session.query(LabelsAlchemy).distinct(LabelsAlchemy.label, LabelsAlchemy.family)
    query = query.filter(LabelsAlchemy.experiment_id == experiment_id)
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

def getFamiliesCounts(session, experiment_id, iteration_max = None, label = None):
    query = session.query(LabelsAlchemy.family, func.count(LabelsAlchemy.family))
    query = query.filter(LabelsAlchemy.experiment_id == experiment_id)
    if iteration_max is not None:
        query = query.filter(LabelsAlchemy.iteration <= iteration_max)
    if label is not None:
        query = query.filter(LabelsAlchemy.label == label)
    query = query.group_by(LabelsAlchemy.family)
    family_counts = {}
    for r in query.all():
        family_counts[r[0]] = r[1]
    return family_counts

def getLabelFamilyIds(session, experiment_id, label, family = None,
                      iteration_max = None, instance_ids = None):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.experiment_id == experiment_id)
    query = query.filter(LabelsAlchemy.label == label)
    if family is not None:
        query = query.filter(LabelsAlchemy.family == family)
    if iteration_max is not None:
        query = query.filter(LabelsAlchemy.iteration <= iteration_max)
    if instance_ids is not None:
        query = query.filter(LabelsAlchemy.instance_id.in_(instance_ids))
    instance_ids = [r.instance_id for r in query.all()]
    return instance_ids

def getLabelIds(session, label, experiment_id, annotation = False):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.label == label)
    if experiment_id is not None:
        query = query.filter(LabelsAlchemy.experiment_id == experiment_id)
        if annotation:
            query= query.filter(LabelsAlchemy.annotation)
    instance_ids = [r.instance_id for r in query.all()]
    return instance_ids

def getAssociatedLabel(session, family, experiment_id):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.experiment_id == experiment_id)
    query = query.filter(LabelsAlchemy.family == str(family)) # MySQL does not support unicode_ type
    query = query.limit(1)
    res = query.one()
    return res.label

def getUnlabeledIds(session, experiment_id, instance_ids = None,
                    iteration_max = None):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.experiment_id == experiment_id)
    if iteration_max is not None:
        query = query.filter(LabelsAlchemy.iteration <= iteration_max)
    if instance_ids is not None:
        query = query.filter(LabelsAlchemy.instance_id.in_(instance_ids))
    instance_ids = [r.instance_id for r in query.all()]
    return instance_ids

#####################
### Update Labels ###
#####################

def addLabel(session, experiment_id, dataset_id, instance_id, label,
        family, iteration_number, method, annotation):
    label = LabelsAlchemy(experiment_id = experiment_id,
                          dataset_id = dataset_id,
                          instance_id = int(instance_id), # MySQL does not support numpy types (int64)
                          label = label,
                          family = family,
                          iteration = iteration_number,
                          method = method,
                          annotation = annotation)
    session.add(label)
    session.commit()

def removeLabel(session, experiment_id, instance_id):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.instance_id == instance_id)
    query = query.filter(LabelsAlchemy.experiment_id == experiment_id)
    try:
        label = query.one()
        session.delete(label)
        session.commit()
    except NoResultFound:
        return None

#####################
### Edit Families ###
#####################

def changeFamilyName(session, label, family, new_family_name, experiment_id):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.label == label)
    query = query.filter(LabelsAlchemy.family == family)
    query = query.filter(LabelsAlchemy.experiment_id == experiment_id)
    instances = query.all()
    for instance in instances:
        instance.family = new_family_name
    session.commit()

def changeFamilyLabel(session, label, family, experiment_id):
    query = session.query(LabelsAlchemy)
    query = query.filter(LabelsAlchemy.label == label)
    query = query.filter(LabelsAlchemy.family == family)
    query = query.filter(LabelsAlchemy.experiment_id == experiment_id)
    instances = query.all()
    new_label = labelBooleanToString(not(labelStringToBoolean(label)))
    for instance in instances:
        instance.label = new_label
    session.commit()

def mergeFamilies(session, label, families, new_family_name, experiment_id):
    for family in families:
        changeFamilyName(session, label, family, new_family_name, experiment_id)
