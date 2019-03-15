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

import argparse

from secuml.core.projection.conf import algos as projection_conf
from secuml.exp.conf.annotations import AnnotationsConf
from secuml.exp.conf.dataset import DatasetConf
from secuml.exp.conf.exp import ExpConf
from secuml.exp.conf.features import FeaturesConf


class ProjectionConf(ExpConf):

    @staticmethod
    def gen_parser():
        parser = argparse.ArgumentParser(
            description='Projection of the data for data visualization.')
        ExpConf.gen_parser(parser)
        AnnotationsConf.gen_parser(
                 parser,
                 message='CSV file containing the annotations of some'
                         ' instances. These annotations are used for '
                         'semi-supervised projections.')
        subparsers = parser.add_subparsers(dest='algo')
        subparsers.required = True
        for algo in projection_conf.get_factory().get_methods():
            algo_parser = subparsers.add_parser(algo)
            projection_conf.get_factory().gen_parser(algo, algo_parser)
        return parser

    @staticmethod
    def from_args(args):
        secuml_conf = ExpConf.common_from_args(args)
        dataset_conf = DatasetConf.from_args(args, secuml_conf.logger)
        features_conf = FeaturesConf.from_args(args, secuml_conf.logger)
        annotations_conf = AnnotationsConf(args.annotations_file, None,
                                           secuml_conf.logger)
        core_conf = projection_conf.get_factory().from_args(args.algo, args,
                                                            secuml_conf.logger)
        return ProjectionConf(secuml_conf, dataset_conf, features_conf,
                              annotations_conf, core_conf, name=args.exp_name)

    def from_json(conf_json, secuml_conf):
        dataset_conf = DatasetConf.from_json(conf_json['dataset_conf'],
                                             secuml_conf.logger)
        features_conf = FeaturesConf.from_json(conf_json['features_conf'],
                                               secuml_conf.logger)
        annotations_conf = AnnotationsConf.from_json(
                                                 conf_json['annotations_conf'],
                                                 secuml_conf.logger)
        core_conf = projection_conf.get_factory().from_json(
                                                    conf_json['core_conf'],
                                                    secuml_conf.logger)
        conf = ProjectionConf(secuml_conf, dataset_conf, features_conf,
                              annotations_conf, core_conf,
                              name=conf_json['name'],
                              parent=conf_json['parent'])
        conf.exp_id = conf_json['exp_id']
        return conf
