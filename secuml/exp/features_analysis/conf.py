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

import argparse

from secuml.exp.conf.annotations import AnnotationsConf
from secuml.exp.conf.dataset import DatasetConf
from secuml.exp.conf.exp import ExpConf
from secuml.exp.conf.features import FeaturesConf


class FeaturesAnalysisConf(ExpConf):

    @staticmethod
    def gen_parser():
        parser = argparse.ArgumentParser(description='Features Analysis')
        ExpConf.gen_parser(parser, filters=False)
        AnnotationsConf.gen_parser(
                    parser, required=False,
                    message='CSV file containing the annotations of some or all'
                            ' the instances.')
        return parser

    @staticmethod
    def from_args(args):
        secuml_conf = ExpConf.common_from_args(args)
        dataset_conf = DatasetConf.from_args(args, secuml_conf.logger)
        features_conf = FeaturesConf.from_args(args, secuml_conf.logger)
        annotations_conf = AnnotationsConf(args.annotations_file, None,
                                           secuml_conf.logger)
        return FeaturesAnalysisConf(secuml_conf, dataset_conf,
                                    features_conf, annotations_conf, None,
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
        conf = FeaturesAnalysisConf(secuml_conf, dataset_conf, features_conf,
                                    annotations_conf, None,
                                    name=conf_json['name'],
                                    parent=conf_json['parent'])
        conf.exp_id = conf_json['exp_id']
        return conf
