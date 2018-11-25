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
import os.path as path

from SecuML.core.Conf import Conf
from SecuML.core.Conf import exportFieldMethod
from SecuML.core.tools import dir_tools

from SecuML.exp.SecuMLConf import SecuMLConf

from .DatasetConf import DatasetConf
from .FeaturesConf import FeaturesConf


class ExpConf(Conf):

    def __init__(self, secuml_conf, dataset_conf, features_conf,
                 annotations_conf, core_conf, experiment_name=None,
                 parent=None):
        Conf.__init__(self, secuml_conf.logger)
        self.secuml_conf = secuml_conf
        self.dataset_conf = dataset_conf
        self.features_conf = features_conf
        self.annotations_conf = annotations_conf
        self.core_conf = core_conf
        self.experiment_name = experiment_name
        self.experiment_id = None
        self.parent = parent
        self._set_exp_name()

    def output_dir(self):
        return path.join(self.dataset_conf.output_dir(self.secuml_conf),
                         str(self.experiment_id))

    def export(self):
        experiment_dir = self.output_dir()
        dir_tools.createDirectory(experiment_dir)
        conf_filename = path.join(experiment_dir, 'conf.json')
        with open(conf_filename, 'w') as f:
            json.dump(self.to_json(), f, indent=2)

    def getKind(self):
        return self.__class__.__name__.split('Conf')[0]

    def _set_exp_name(self):
        if self.experiment_name is not None:
            return
        self.experiment_name = self._get_exp_name()

    def _get_exp_name(self):
        name = ''
        if self.core_conf is not None:
            name += self.core_conf.get_exp_name()
        basename, ext = path.splitext(self.features_conf.input_features)
        if name != '':
            name += '__'
        name += 'Features_' + basename
        return name

    def set_dataset_id(self, dataset_id, session):
        self.dataset_conf.set_dataset_id(dataset_id, session)

    def set_experiment_id(self, experiment_id):
        self.experiment_id = experiment_id

    def set_exp_annotations(self, annotations_id, annotations_type):
        self.annotations_conf.set_exp_annotations(annotations_id,
                                                  annotations_type)

    def fieldsToExport(self):
        return [('dataset_conf', exportFieldMethod.obj),
                ('features_conf', exportFieldMethod.obj),
                ('annotations_conf', exportFieldMethod.obj),
                ('core_conf', exportFieldMethod.obj),
                ('experiment_name', exportFieldMethod.primitive),
                ('parent', exportFieldMethod.primitive),
                ('experiment_id', exportFieldMethod.primitive)]

    @staticmethod
    def common_from_args(args):
        secuml_conf = SecuMLConf(args.secuml_conf)
        return secuml_conf

    @staticmethod
    def generateParser(parser, filters=True):
        DatasetConf.generateParser(parser)
        parser.add_argument('--exp-name', type=str,
                            required=False,
                            default=None,
                            help='Name of the experiment. '
                                 'If not provided, a default name is '
                                 'automatically generated from the input '
                                 'parameters.')
        parser.add_argument('--secuml-conf', type=str,
                            required=False,
                            default=None,
                            help='YAML file containing the configuration. '
                                 'If --secuml-conf is not set, the '
                                 'configuration is read from the file stored '
                                 'in the environment variable SECUMLCONF.')
        FeaturesConf.generateParser(parser, filters=filters)
