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

from SecuML.core.Conf import exportFieldMethod
from SecuML.core.clustering.conf import ClusteringConfFactory
from SecuML.exp.conf.AnnotationsConf import AnnotationsConf
from SecuML.exp.conf.DatasetConf import DatasetConf
from SecuML.exp.conf.ExpConf import ExpConf
from SecuML.exp.conf.FeaturesConf import FeaturesConf


class ClusteringConf(ExpConf):

    def __init__(self, secuml_conf, dataset_conf, features_conf,
                 annotations_conf, core_conf, experiment_name=None,
                 parent=None, label='all'):
        ExpConf.__init__(self, secuml_conf, dataset_conf, features_conf,
                         annotations_conf, core_conf,
                         experiment_name=experiment_name, parent=parent)
        self.label = label

    def fieldsToExport(self):
        fields = ExpConf.fieldsToExport(self)
        fields.extend([('label', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(
            description='Clustering of the data for data exploration.')
        ExpConf.generateParser(parser)
        AnnotationsConf.generateParser(parser,
                    message='CSV file containing the annotations of some '
                            'instances. These annotations are used for '
                            'semi-supervised projections.')
        parser.add_argument('--label',
                 choices=['all', 'malicious', 'benign'],
                 default='all',
                 help='The clustering is built from all the instances in the '
                      'dataset, or only from the benign or malicious ones. '
                      'By default, the clustering is built from all the '
                      'instances. The malicious and benign instances are '
                      'selected according to the ground-truth stored in '
                      'annotations/ground_truth.csv.')
        subparsers = parser.add_subparsers(dest='algo')
        subparsers.required = True
        factory = ClusteringConfFactory.getFactory()
        for algo in factory.getMethods():
            algo_parser = subparsers.add_parser(algo)
            factory.generateParser(algo, algo_parser)
        return parser

    @staticmethod
    def fromArgs(args):
        secuml_conf = ExpConf.common_from_args(args)
        dataset_conf = DatasetConf.fromArgs(args, secuml_conf.logger)
        features_conf = FeaturesConf.fromArgs(args, secuml_conf.logger)
        annotations_conf = AnnotationsConf(args.annotations_file, None,
                                           secuml_conf.logger)
        factory = ClusteringConfFactory.getFactory()
        core_conf = factory.fromArgs(args.algo, args, secuml_conf.logger)
        conf = ClusteringConf(secuml_conf, dataset_conf, features_conf,
                              annotations_conf, core_conf,
                              experiment_name=args.exp_name,
                              label=args.label)
        return conf

    def from_json(conf_json, secuml_conf):
        dataset_conf = DatasetConf.from_json(conf_json['dataset_conf'],
                                             secuml_conf.logger)
        features_conf = FeaturesConf.from_json(conf_json['features_conf'],
                                               secuml_conf.logger)
        annotations_conf = AnnotationsConf.from_json(
                                                  conf_json['annotations_conf'],
                                                  secuml_conf.logger)
        factory = ClusteringConfFactory.getFactory()
        core_conf = None
        if conf_json['core_conf'] is not None:
            core_conf = factory.from_json(conf_json['core_conf'],
                                          secuml_conf.logger)
        exp_conf = ClusteringConf(secuml_conf,
                                  dataset_conf,
                                  features_conf,
                                  annotations_conf,
                                  core_conf,
                                  experiment_name=conf_json['experiment_name'],
                                  parent=conf_json['parent'],
                                  label=conf_json['label'])
        exp_conf.experiment_id = conf_json['experiment_id']
        return exp_conf
