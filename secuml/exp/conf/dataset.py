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

from secuml.core.conf import Conf
from secuml.core.conf import exportFieldMethod


class DatasetConf(Conf):

    def __init__(self, project, dataset, logger):
        Conf.__init__(self, logger)
        self.project = project
        self.dataset = dataset
        self.dataset_id = None
        self.has_ground_truth = None

    def input_dir(self, secuml_conf):
        return os.path.join(secuml_conf.input_data_dir, self.project,
                            self.dataset)

    def output_dir(self, secuml_conf):
        return os.path.join(secuml_conf.output_data_dir, self.project,
                            self.dataset)

    def set_dataset_id(self, dataset_id, session):
        self.dataset_id = dataset_id

    def set_has_ground_truth(self, has_ground_truth):
        self.has_ground_truth = has_ground_truth

    def fields_to_export(self):
        return [('project', exportFieldMethod.primitive),
                ('dataset', exportFieldMethod.primitive),
                ('dataset_id', exportFieldMethod.primitive),
                ('has_ground_truth', exportFieldMethod.primitive)]

    @staticmethod
    def gen_parser(parser):
        parser.add_argument('project')
        parser.add_argument('dataset')

    @staticmethod
    def from_args(args, logger):
        return DatasetConf(args.project, args.dataset, logger)

    @staticmethod
    def from_json(conf_json, logger):
        conf = DatasetConf(conf_json['project'], conf_json['dataset'], logger)
        conf.dataset_id = conf_json['dataset_id']
        conf.has_ground_truth = conf_json['has_ground_truth']
        return conf
