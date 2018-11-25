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

from SecuML.core.classification.conf import ClassifierConfFactory
from SecuML.core.classification.conf.ClassificationConf \
        import ClassificationConf as CoreClassificationConf
from SecuML.core.Conf import exportFieldMethod
from SecuML.exp.conf.AnnotationsConf import AnnotationsConf
from SecuML.exp.conf.DatasetConf import DatasetConf
from SecuML.exp.conf.ExpConf import ExpConf
from SecuML.exp.conf.FeaturesConf import FeaturesConf


class ClassificationConf(ExpConf):

    def __init__(self, secuml_conf, dataset_conf, features_conf,
                 annotations_conf, core_conf, experiment_name=None,
                 parent=None, already_trained=None):
        self.already_trained = already_trained
        ExpConf.__init__(self, secuml_conf, dataset_conf, features_conf,
                         annotations_conf, core_conf,
                         experiment_name=experiment_name, parent=parent)
        self.test_exp_conf = None

    def fieldsToExport(self):
        fields = ExpConf.fieldsToExport(self)
        fields.extend([('already_trained', exportFieldMethod.primitive)])
        fields.extend([('test_exp_conf', exportFieldMethod.obj)])
        return fields

    def _get_exp_name(self):
        name = ''
        if self.already_trained is not None:
            name += 'AlreadyTrained_exp%i' % self.already_trained
        name += ExpConf._get_exp_name(self)
        return name

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(
            description='Learn a detection model. '
                        'The ground-truth must be stored in '
                        'annotations/ground_truth.csv.')
        ExpConf.generateParser(parser)
        CoreClassificationConf.generateParser(parser)
        models = ['LogisticRegression', 'Svc', 'GaussianNaiveBayes',
                 'DecisionTree', 'RandomForest', 'GradientBoosting']
        subparsers = parser.add_subparsers(dest='model_class')
        subparsers.required = True
        factory = ClassifierConfFactory.getFactory()
        for model in models:
            model_parser = subparsers.add_parser(model)
            factory.generateParser(model, model_parser)
            AnnotationsConf.generateParser(model_parser,
                        required=True,
                        message='CSV file containing the annotations of some '
                                'or all the instances.')
        ## Add subparser for already trained model
        already_trained = subparsers.add_parser('AlreadyTrained')
        factory.generateParser('AlreadyTrained', already_trained)
        return parser

    @staticmethod
    def fromArgs(args):
        secuml_conf = ExpConf.common_from_args(args)
        already_trained = None
        if args.model_class != 'AlreadyTrained':
            core_conf = CoreClassificationConf.fromArgs(args, True,
                                                        secuml_conf.logger)
            annotations_conf = AnnotationsConf(args.annotations_file, None,
                                               secuml_conf.logger)
        else:
            already_trained = args.model_exp_id
            core_conf = CoreClassificationConf.fromArgs(args, False,
                                                        secuml_conf.logger)
            annotations_conf = AnnotationsConf(None, None, secuml_conf.logger)
        dataset_conf = DatasetConf.fromArgs(args, secuml_conf.logger)
        features_conf = FeaturesConf.fromArgs(args, secuml_conf.logger)
        return ClassificationConf(secuml_conf, dataset_conf, features_conf,
                                  annotations_conf, core_conf,
                                  experiment_name=args.exp_name,
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
        core_conf = CoreClassificationConf.from_json(conf_json['core_conf'],
                                                     secuml_conf.logger)
        exp_conf = ClassificationConf(secuml_conf,
                                  dataset_conf,
                                  features_conf,
                                  annotations_conf,
                                  core_conf,
                                  experiment_name=conf_json['experiment_name'],
                                  parent=conf_json['parent'],
                                  already_trained=conf_json['already_trained'])
        exp_conf.experiment_id = conf_json['experiment_id']
        return exp_conf
