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

from secuml.core.classif.conf import classifiers
from secuml.core.classif.conf import ClassificationConf
from secuml.core.conf import exportFieldMethod
from secuml.exp.conf.annotations import AnnotationsConf
from secuml.exp.conf.dataset import DatasetConf
from secuml.exp.conf.exp import ExpConf
from secuml.exp.conf.features import FeaturesConf


class DiademConf(ExpConf):

    def __init__(self, secuml_conf, dataset_conf, features_conf,
                 annotations_conf, core_conf, name=None, parent=None,
                 already_trained=None):
        self.already_trained = already_trained
        ExpConf.__init__(self, secuml_conf, dataset_conf, features_conf,
                         annotations_conf, core_conf, name=name, parent=parent)

    def fields_to_export(self):
        fields = ExpConf.fields_to_export(self)
        fields.extend([('already_trained', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def gen_parser():
        parser = argparse.ArgumentParser(
            description='Learn a detection model. '
                        'The ground-truth must be stored in '
                        'annotations/ground_truth.csv.')
        ExpConf.gen_parser(parser)
        ClassificationConf.gen_parser(parser)
        factory = classifiers.get_factory()
        models = factory.get_methods()
        models.remove('AlreadyTrained')
        subparsers = parser.add_subparsers(dest='model_class')
        subparsers.required = True
        for model in models:
            model_parser = subparsers.add_parser(model)
            factory.gen_parser(model, model_parser)
            AnnotationsConf.gen_parser(
                        model_parser, required=False,
                        message='CSV file containing the annotations of some '
                                'or all the instances.')
        # Add subparser for already trained model
        already_trained = subparsers.add_parser('AlreadyTrained')
        factory.gen_parser('AlreadyTrained', already_trained)
        return parser

    @staticmethod
    def from_args(args):
        secuml_conf = ExpConf.secuml_conf_from_args(args)
        already_trained = None
        core_conf = ClassificationConf.from_args(args, secuml_conf.logger)
        if args.model_class != 'AlreadyTrained':
            annotations_conf = AnnotationsConf(args.annotations_file, None,
                                               secuml_conf.logger)
        else:
            already_trained = args.model_exp_id
            annotations_conf = AnnotationsConf(None, None, secuml_conf.logger)
        dataset_conf = DatasetConf.from_args(args, secuml_conf.logger)
        features_conf = FeaturesConf.from_args(args, secuml_conf.logger)
        return DiademConf(secuml_conf, dataset_conf, features_conf,
                          annotations_conf, core_conf, name=args.exp_name,
                          already_trained=already_trained)

    @staticmethod
    def from_json(conf_json, secuml_conf):
        dataset_conf = DatasetConf.from_json(conf_json['dataset_conf'],
                                             secuml_conf.logger)
        features_conf = FeaturesConf.from_json(conf_json['features_conf'],
                                               secuml_conf.logger)
        annotations_conf = AnnotationsConf.from_json(
                                                 conf_json['annotations_conf'],
                                                 secuml_conf.logger)
        core_conf = ClassificationConf.from_json(conf_json['core_conf'],
                                                 secuml_conf.logger)
        exp_conf = DiademConf(secuml_conf, dataset_conf, features_conf,
                              annotations_conf, core_conf,
                              name=conf_json['name'],
                              parent=conf_json['parent'],
                              already_trained=conf_json['already_trained'])
        exp_conf.exp_id = conf_json['exp_id']
        return exp_conf
