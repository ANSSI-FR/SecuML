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

import json
import os
import shutil
from sqlalchemy.orm.exc import NoResultFound

from secuml.core.tools.color import display_in_green

from .data.dataset import Dataset
from .data.instances import Instances
from .tools.db_tables import ExpAlchemy
from .tools.db_tables import ExpRelationshipsAlchemy
from .tools.exp_exceptions import SecuMLexpException


class NotMainExperiment(SecuMLexpException):

    def __init__(self, exp_id):
        self.exp_id = exp_id

    def __str__(self):
        return('The experiment %i is not a main experiment. '
               'It cannot be deleted. ' % self.exp_id)


class UndefinedExperiment(SecuMLexpException):

    def __init__(self, exp_id):
        self.exp_id = exp_id

    def __str__(self):
        return 'There is no experiment with the id %i.' % self.exp_id


class Experiment(object):

    def __init__(self, exp_conf, create=True, session=None):
        self.exp_conf = exp_conf
        self.logger = self.exp_conf.secuml_conf.logger
        self._set_session(session)
        self.exp_id = exp_conf.exp_id
        self.create = create

    def _set_session(self, session):
        if session is None:
            self.session = self.exp_conf.secuml_conf.Session()
        else:
            self.session = session

    def output_dir(self):
        return self.exp_conf.output_dir()

    def get_instances(self, instances=None):
        if instances is None:
            instances = Instances(self)
        return instances

    def run(self):
        if self.create:
            self.create_exp()
        if self.exp_conf.parent is None:
            self.logger.info('Experiment n°%d', self.exp_conf.exp_id)

    def rollback_session(self):
        self.session.rollback()
        self.session.close()
        if self.exp_id is not None:
            self._remove_output_dir()

    def _remove_output_dir(self):
        output_dir = self.output_dir()
        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)

    def close(self):
        self.close_session()
        print(display_in_green(
                '\nExperiment %d has been successfully completed. \n'
                'See http://localhost:5000/SecuML/%d/ '
                'to display the results. \n' %
                (self.exp_id, self.exp_id)))

    def close_session(self):
        self.session.commit()
        self.session.close()
        self.exp_conf.secuml_conf.close_log_handler()

    def remove(self, check_main=True):
        if check_main and self.exp_conf.parent is not None:
            raise NotMainExperiment(self.exp_conf.exp_id)
        # Remove from the DB
        query = self.session.query(ExpAlchemy)
        query = query.filter(ExpAlchemy.id == self.exp_id)
        exp_row = query.one()
        self._remove_children(exp_row)
        self.session.delete(exp_row)
        # Remove the output directory
        self._remove_output_dir()

    def _remove_children(self, exp):
        children = [(c, c.child_id, len(c.child.parents))
                    for c in exp.children]
        for child, child_id, num_parents in children:
            self.session.delete(child)
            if num_parents > 1:
                continue
            self.session.commit()
            child_exp = get_factory().from_exp_id(child_id,
                                                  self.exp_conf.secuml_conf,
                                                  self.session)
            child_exp.remove(check_main=False)

    def create_exp(self):
        # Load idents, annotations, features
        exp_dataset = Dataset(self.exp_conf, self.session)
        exp_dataset.load()
        self.session.commit()
        # Add the experiment to the database
        self.add_to_db()
        # Export the configuration
        self.exp_conf.export()

    def add_to_db(self):
        annotations_id = self.exp_conf.annotations_conf.annotations_id
        exp = ExpAlchemy(kind=self.exp_conf.get_kind(),
                         name=self.exp_conf.name,
                         features_set_id=self.exp_conf.features_conf.set_id,
                         annotations_id=annotations_id)
        self.session.add(exp)
        self.session.flush()
        self.exp_conf.set_exp_id(exp.id)
        self.exp_id = exp.id
        if self.exp_conf.parent is not None:
            exp_relation = ExpRelationshipsAlchemy(
                                                child_id=self.exp_id,
                                                parent_id=self.exp_conf.parent)
            self.session.add(exp_relation)

    @staticmethod
    def get_output_dir(secuml_conf, project, dataset, exp_id):
        return os.path.join(secuml_conf.output_data_dir, project, dataset,
                            str(exp_id))


experiment_factory = None


def get_factory():
    global experiment_factory
    if experiment_factory is None:
        experiment_factory = ExpFactory()
    return experiment_factory


def get_project_dataset(session, exp_id):
    query = session.query(ExpAlchemy)
    query = query.filter(ExpAlchemy.id == exp_id)
    try:
        exp = query.one()
    except NoResultFound:
        raise UndefinedExperiment(exp_id)
    dataset = exp.features_set.dataset
    return dataset.project, dataset.dataset


class ExpFactory(object):

    def __init__(self):
        self.classes = {}

    def register(self, class_name, exp_class, conf_class):
        self.classes[class_name] = (exp_class, conf_class)

    def from_exp_id(self, exp_id, secuml_conf, session):
        project, dataset = get_project_dataset(session, exp_id)
        conf_filename = os.path.join(secuml_conf.output_data_dir, project,
                                     dataset, str(exp_id), 'conf.json')
        with open(conf_filename, 'r') as conf_file:
            conf_json = json.load(conf_file)
            class_name = conf_json['__type__'].split('Conf')[0]
            exp_class, conf_class = self.classes[class_name]
            exp_conf = conf_class.from_json(conf_json, secuml_conf)
            return exp_class(exp_conf, create=False, session=session)
