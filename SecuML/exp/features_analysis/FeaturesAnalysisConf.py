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

from SecuML.exp.conf.AnnotationsConf import AnnotationsConf
from SecuML.exp.conf.DatasetConf import DatasetConf
from SecuML.exp.conf.ExpConf import ExpConf
from SecuML.exp.conf.FeaturesConf import FeaturesConf


class FeaturesAnalysisConf(ExpConf):

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(description='Features Analysis')
        ExpConf.generateParser(parser, filters=False)
        AnnotationsConf.generateParser(parser,
                    required=True,
                    message='CSV file containing the annotations of some or all'
                            ' the instances.')
        return parser

    @staticmethod
    def fromArgs(args):
        secuml_conf = ExpConf.common_from_args(args)
        dataset_conf = DatasetConf.fromArgs(args, secuml_conf.logger)
        features_conf = FeaturesConf.fromArgs(args, secuml_conf.logger)
        annotations_conf = AnnotationsConf(args.annotations_file, None,
                                           secuml_conf.logger)
        return FeaturesAnalysisConf(secuml_conf, dataset_conf,
                                    features_conf, annotations_conf, None,
                                    experiment_name=args.exp_name)

    @staticmethod
    def from_json(conf_json, secuml_conf):
        dataset_conf = DatasetConf.from_json(conf_json['dataset_conf'],
                                             secuml_conf.logger)
        features_conf = FeaturesConf.from_json(conf_json['features_conf'],
                                               secuml_conf.logger)
        annotations_conf = AnnotationsConf.from_json(
                                                  conf_json['annotations_conf'],
                                                  secuml_conf.logger)
        conf = FeaturesAnalysisConf(secuml_conf,
                                    dataset_conf,
                                    features_conf,
                                    annotations_conf,
                                    None,
                                    experiment_name=conf_json['experiment_name'],
                                    parent=conf_json['parent'])
        conf.experiment_id = conf_json['experiment_id']
        return conf
