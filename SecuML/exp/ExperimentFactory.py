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

import json
import os

from SecuML.exp.tools import db_tools

experiment_factory = None


def getFactory():
    global experiment_factory
    if experiment_factory is None:
        experiment_factory = ExperimentFactory()
    return experiment_factory


class ExperimentFactory(object):

    def __init__(self):
        self.classes = {}

    def register(self, class_name, exp_class, conf_class):
        self.classes[class_name] = (exp_class, conf_class)

    def from_exp_id(self, exp_id, secuml_conf, session):
        project, dataset = db_tools.getProjectDataset(session, exp_id)
        conf_filename = os.path.join(secuml_conf.output_data_dir, project,
                                     dataset, str(exp_id), 'conf.json')
        with open(conf_filename, 'r') as conf_file:
            conf_json = json.load(conf_file)
            class_name = conf_json['__type__'].split('Conf')[0]
            exp_class, conf_class = self.classes[class_name]
            exp_conf = conf_class.from_json(conf_json, secuml_conf)
            exp = exp_class(exp_conf, create=False, session=session)
            return exp
