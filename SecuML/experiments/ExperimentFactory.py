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

from SecuML.experiments import experiment_db_tools
from SecuML.experiments.Tools import dir_exp_tools

experiment_factory = None


def getFactory():
    global experiment_factory
    if experiment_factory is None:
        experiment_factory = ExperimentFactory()
    return experiment_factory


class ExperimentFactory(object):

    def __init__(self):
        self.register = {}

    def registerClass(self, class_name, class_obj):
        self.register[class_name] = class_obj

    def fromJson(self, experiment_id, session):
        project, dataset = experiment_db_tools.getProjectDataset(session,
                                                                 experiment_id)
        obj_filename = dir_exp_tools.getExperimentConfigurationFilename(project,
                                                                        dataset,
                                                                        experiment_id)
        with open(obj_filename, 'r') as obj_file:
            obj_dict = json.load(obj_file)
            class_name = obj_dict['__type__']
            obj = self.register[class_name].fromJson(obj_dict, session)
        return obj
