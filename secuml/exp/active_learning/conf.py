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

from secuml.core.active_learning.conf import strategies as strategies_conf
from secuml.exp.conf.annotations import AnnotationsConf
from secuml.exp.conf.dataset import DatasetConf
from secuml.exp.conf.exp import ExpConf
from secuml.exp.conf.features import FeaturesConf


class ActiveLearningConf(ExpConf):

    @staticmethod
    def gen_parser():
        parser = argparse.ArgumentParser(
                description='Active Learning',
                formatter_class=argparse.RawTextHelpFormatter)
        ExpConf.gen_parser(parser)
        AnnotationsConf.gen_parser(
                    parser, default='init_annotations.csv', required=False,
                    message='CSV file containing the initial annotations '
                            'used to learn the first supervised detection '
                            'model.')
        subparsers = parser.add_subparsers(dest='strategy')
        subparsers.required = True
        strategies = strategies_conf.get_factory().get_methods()
        for strategy in strategies:
            strategy_parser = subparsers.add_parser(strategy)
            strategies_conf.get_factory().gen_parser(strategy, strategy_parser)
        return parser

    @staticmethod
    def from_args(args):
        secuml_conf = ExpConf.common_from_args(args)
        dataset_conf = DatasetConf.from_args(args, secuml_conf.logger)
        features_conf = FeaturesConf.from_args(args, secuml_conf.logger)
        annotations_conf = AnnotationsConf(args.annotations_file, None,
                                           secuml_conf.logger)
        core_conf = strategies_conf.get_factory().from_args(args.strategy,
                                                            args,
                                                            secuml_conf.logger)
        return ActiveLearningConf(secuml_conf, dataset_conf, features_conf,
                                  annotations_conf, core_conf,
                                  name=args.exp_name)

    @staticmethod
    def from_json(conf_json, secuml_conf):
        dataset_conf = DatasetConf.from_json(conf_json['dataset_conf'],
                                             secuml_conf.logger)
        features_conf = FeaturesConf.from_json(conf_json['features_conf'],
                                               secuml_conf.logger)
        annotations_conf = AnnotationsConf.from_json(
                                                 conf_json['annotations_conf'],
                                                 secuml_conf.logger)
        core_conf = strategies_conf.get_factory().from_json(
                                                        conf_json['core_conf'],
                                                        secuml_conf.logger)
        conf = ActiveLearningConf(secuml_conf, dataset_conf, features_conf,
                                  annotations_conf, core_conf,
                                  name=conf_json['name'],
                                  parent=conf_json['parent'])
        conf.exp_id = conf_json['exp_id']
        return conf


class RcdConf(ExpConf):

    @staticmethod
    def gen_parser():
        parser = argparse.ArgumentParser(
                                 description='Rare Category Detection',
                                 formatter_class=argparse.RawTextHelpFormatter)
        ExpConf.gen_parser(parser)
        AnnotationsConf.gen_parser(
                    parser, default='init_annotations.csv', required=False,
                    message='CSV file containing the initial annotations '
                            'used to learn the first supervised detection '
                            'model.')
        strategies_conf.get_factory().gen_parser('Rcd', parser)
        return parser

    @staticmethod
    def from_args(args):
        secuml_conf = ExpConf.common_from_args(args)
        logger = secuml_conf.logger
        dataset_conf = DatasetConf.from_args(args, logger)
        features_conf = FeaturesConf.from_args(args, logger)
        annotations_conf = AnnotationsConf(args.annotations_file, None, logger)
        core_conf = strategies_conf.get_factory().from_args('Rcd', args,
                                                            logger)
        return RcdConf(secuml_conf, dataset_conf, features_conf,
                       annotations_conf, core_conf, name=args.exp_name)

    @staticmethod
    def from_json(conf_json, secuml_conf):
        logger = secuml_conf.logger
        dataset_conf = DatasetConf.from_json(conf_json['dataset_conf'], logger)
        features_conf = FeaturesConf.from_json(conf_json['features_conf'],
                                               logger)
        annotations_conf = AnnotationsConf.from_json(
                                                 conf_json['annotations_conf'],
                                                 logger)
        factory = strategies_conf.get_factory()
        core_conf = factory.from_json(conf_json['core_conf'], logger)
        conf = RcdConf(secuml_conf, dataset_conf, features_conf,
                       annotations_conf, core_conf, name=conf_json['name'],
                       parent=conf_json['parent'])
        conf.exp_id = conf_json['exp_id']
        return conf
