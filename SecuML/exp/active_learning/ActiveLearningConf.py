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

from SecuML.core.active_learning.conf import ActiveLearningConfFactory
from SecuML.core.Conf import exportFieldMethod
from SecuML.exp.conf.AnnotationsConf import AnnotationsConf
from SecuML.exp.conf.DatasetConf import DatasetConf
from SecuML.exp.conf.ExpConf import ExpConf
from SecuML.exp.conf.FeaturesConf import FeaturesConf


class ActiveLearningConf(ExpConf):

    def __init__(self, secuml_conf, dataset_conf, features_conf,
                 annotations_conf, core_conf, experiment_name=None,
                 parent=None):
        ExpConf.__init__(self, secuml_conf, dataset_conf, features_conf,
                         annotations_conf, core_conf,
                         experiment_name=experiment_name, parent=parent)
        self.test_exp_conf = None

    def fieldsToExport(self):
        fields = ExpConf.fieldsToExport(self)
        fields.extend([('test_exp_conf', exportFieldMethod.obj)])
        return fields

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(
                description='Active Learning',
                formatter_class=argparse.RawTextHelpFormatter)
        ExpConf.generateParser(parser)
        AnnotationsConf.generateParser(parser,
                    default='init_annotations.csv',
                    required=False,
                    message='CSV file containing the initial annotations '
                            'used to learn the first supervised detection '
                            'model.')
        subparsers = parser.add_subparsers(dest='strategy')
        subparsers.required = True
        factory = ActiveLearningConfFactory.getFactory()
        strategies = factory.getMethods()
        for strategy in strategies:
            strategy_parser = subparsers.add_parser(strategy)
            factory.generateParser(strategy, strategy_parser)
        return parser

    @staticmethod
    def fromArgs(args):
        secuml_conf = ExpConf.common_from_args(args)
        dataset_conf = DatasetConf.fromArgs(args, secuml_conf.logger)
        features_conf = FeaturesConf.fromArgs(args, secuml_conf.logger)
        annotations_conf = AnnotationsConf(args.annotations_file, None,
                                           secuml_conf.logger)
        factory = ActiveLearningConfFactory.getFactory()
        core_conf = factory.fromArgs(args.strategy, args, secuml_conf.logger)
        return ActiveLearningConf(secuml_conf, dataset_conf, features_conf,
                                  annotations_conf, core_conf,
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
        factory = ActiveLearningConfFactory.getFactory()
        core_conf = factory.from_json(conf_json['core_conf'],
                                      secuml_conf.logger)
        conf = ActiveLearningConf(secuml_conf,
                                  dataset_conf,
                                  features_conf,
                                  annotations_conf,
                                  core_conf,
                                  experiment_name=conf_json['experiment_name'],
                                  parent=conf_json['parent'])
        conf.experiment_id = conf_json['experiment_id']
        return conf
