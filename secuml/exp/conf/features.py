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

from enum import Enum

from secuml.core.conf import Conf
from secuml.core.conf import exportFieldMethod


class InputFeaturesTypes(Enum):
    file = 0
    dir = 1


class FeaturesConf(Conf):

    def __init__(self, input_features, logger, filter_in_filename=None,
                 filter_out_filename=None):
        Conf.__init__(self, logger)
        self.input_features = input_features
        self.filter_in_filename = filter_in_filename
        self.filter_out_filename = filter_out_filename
        self.input_type = None
        self.features_set_id = None
        self.features_files_ids = []
        self.filter_in = None
        self.filter_out = None

    def fields_to_export(self):
        return [('input_features', exportFieldMethod.primitive),
                ('input_type', exportFieldMethod.enum_value),
                ('features_set_id', exportFieldMethod.primitive),
                ('features_files_ids', exportFieldMethod.primitive),
                ('filter_in', exportFieldMethod.primitive),
                ('filter_out', exportFieldMethod.primitive)]

    @staticmethod
    def gen_parser(parser, filters=True):
        group = parser
        if filters:
            group = parser.add_argument_group('Features')
        group.add_argument(
                 '--features', '-f', dest='input_features', required=False,
                 default='features.csv',
                 help='CSV file containing the features or a directory. '
                      'In the latter case, all the files of the directory are '
                      'concatenated to build the input features. '
                      'Default: features.csv. ')
        if filters:
            filter_group = group.add_mutually_exclusive_group()
            filter_group.add_argument(
                             '--filter-in', required=False, default=None,
                             help='File containing the features to use. '
                                  'File format: one feature id per line. ')
            filter_group.add_argument(
                            '--filter-out', required=False, default=None,
                            help='File containing the features to filter out. '
                                 'File format: one feature id per line. ')

    @staticmethod
    def from_args(args, logger):
        if hasattr(args, 'filter_in'):
            filter_in_filename = args.filter_in
            filter_out_filename = args.filter_out
        else:
            filter_in_filename = None
            filter_out_filename = None
        return FeaturesConf(args.input_features, logger,
                            filter_in_filename=filter_in_filename,
                            filter_out_filename=filter_out_filename)

    @staticmethod
    def from_json(conf_json, logger):
        conf = FeaturesConf(conf_json['input_features'], logger)
        conf.input_type = InputFeaturesTypes[conf_json['input_type']]
        conf.features_set_id = conf_json['features_set_id']
        conf.features_files_ids = conf_json['features_files_ids']
        conf.filter_in = conf_json['filter_in']
        conf.filter_out = conf_json['filter_out']
        return conf
