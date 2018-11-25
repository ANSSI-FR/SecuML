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


import os
import shutil

from SecuML.core.tools import colors_tools

from .db_tables import ExpAlchemy
from .data.ExpDataset import ExpDataset
from .data.InstancesFromExp import InstancesFromExp


class Experiment(object):

    def __init__(self, exp_conf, create=True, session=None):
        self.exp_conf = exp_conf
        self.logger = self.exp_conf.secuml_conf.logger
        self._set_session(session)
        self.experiment_id = exp_conf.experiment_id
        self.create = create

    def _set_session(self, session):
        if session is None:
            self.session = self.exp_conf.secuml_conf.Session()
        else:
            self.session = session

    def output_dir(self):
        return self.exp_conf.output_dir()

    def getInstances(self, instances=None):
        if instances is None:
            instances = InstancesFromExp(self)
        return instances

    def run(self):
        if self.create:
            self.create_exp()
        if self.exp_conf.parent is None:
            self.logger.info('Experiment n°%d', self.exp_conf.experiment_id)

    def rollbackSession(self):
        self.session.rollback()
        self.session.close()
        if self.experiment_id is not None:
            self._remove_output_dir()

    def _remove_output_dir(self):
        output_dir = self.output_dir()
        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)

    def close(self):
        self.close_session()
        print(colors_tools.display_in_green(
                '\nExperiment %d has been successfully completed. \n'
                'See http://localhost:5000/SecuML/%d/ '
                'to display the results. \n' %
                (self.experiment_id, self.experiment_id)))

    def close_session(self):
        self.session.commit()
        self.session.close()
        self.exp_conf.secuml_conf.closeLogHandler()

    def remove(self):
        # Remove from the DB
        query = self.session.query(ExpAlchemy)
        query = query.filter(ExpAlchemy.id == self.experiment_id)
        experiment = query.one()
        self.session.delete(experiment)
        self.session.flush()
        # Remove the output directory
        self._remove_output_dir()

    def create_exp(self):
        # Load idents, annotations, features
        exp_dataset = ExpDataset(self.exp_conf, self.session)
        exp_dataset.load()
        self.session.commit()
        # Add the experiment to the database
        self.add_to_db()
        # Export the configuration
        self.exp_conf.export()

    def add_to_db(self):
        dataset_features_id = self.exp_conf.features_conf.dataset_features_id
        dataset_id = self.exp_conf.dataset_conf.dataset_id
        annotations_id = self.exp_conf.annotations_conf.annotations_id
        exp = ExpAlchemy(kind=self.exp_conf.getKind(),
                         name=self.exp_conf.experiment_name,
                         dataset_id=dataset_id,
                         dataset_features_id=dataset_features_id,
                         annotations_id=annotations_id,
                         parent=self.exp_conf.parent)
        self.session.add(exp)
        self.session.flush()
        self.exp_conf.set_experiment_id(exp.id)
        self.experiment_id = exp.id

    @staticmethod
    def get_output_dir(secuml_conf, project, dataset, exp_id):
        return os.path.join(secuml_conf.output_data_dir, project, dataset,
                            str(exp_id))
