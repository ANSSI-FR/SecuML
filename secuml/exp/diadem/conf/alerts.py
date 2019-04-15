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

from secuml.core.classif.conf import classifiers
from secuml.core.classif.conf.classifiers import ClassifierType
from secuml.core.clustering.conf import algos as cluster_conf
from secuml.core.conf import Conf
from secuml.core.conf import exportFieldMethod
from secuml.core.tools.float import to_percentage


class AlertsConf(Conf):

    def __init__(self, detection_threshold, classifier_conf, clustering_conf,
                 logger):
        Conf.__init__(self, logger)
        self.detection_threshold = detection_threshold
        self.classifier_conf = classifier_conf
        self.clustering_conf = clustering_conf

    def get_exp_name(self):
        name = '__AlertsAnalysis__'
        name += 'threshold_%s__' % to_percentage(self.detection_threshold)
        if self.clustering_conf is not None:
            name += self.clustering_conf.get_exp_name()
        elif self.classifier_conf is not None:
            name += self.classifier_conf.get_exp_name()
        return name

    @staticmethod
    def from_json(obj, logger):
        if obj is None:
            return None
        classifier_conf = None
        clustering_conf = None
        if obj['classifier_conf'] is not None:
            factory = classifiers.get_factory()
            classifier_conf = factory.from_json(obj['classifier_conf'], logger)
        elif obj['clustering_conf'] is not None:
            factory = cluster_conf.get_factory()
            clustering_conf = factory.from_json(obj['clustering_conf'], logger)
        return AlertsConf(obj['detection_threshold'], classifier_conf,
                          clustering_conf, logger)

    def fields_to_export(self):
        return [('detection_threshold', exportFieldMethod.primitive),
                ('classifier_conf', exportFieldMethod.obj),
                ('clustering_conf', exportFieldMethod.obj)]

    @staticmethod
    def gen_parser(parser):
        alerts_group = parser.add_argument_group('Alerts parameters')
        alerts_group.add_argument(
            '--detection-threshold',
            type=float,
            default=0.5,
            help='An alert is triggered if the predicted probability of '
                 'maliciousness is above this threshold. '
                 'Default: 0.5.')
        group = alerts_group.add_mutually_exclusive_group(required=False)
        models = classifiers.get_factory().get_methods(
                                                    ClassifierType.supervised)
        group.add_argument('--alerts-classif',
                           default=None,
                           choices=models,
                           help='Supervised model trained to cluster the '
                                'alerts according to the malicious families '
                                'defined in the training dataset. '
                                'Default: None.')
        group.add_argument('--alerts-clustering',
                           default=None,
                           choices=cluster_conf.get_factory().get_methods(),
                           help='Clustering algorithm to analyze the alerts. '
                                'Default: None.')
        alerts_group.add_argument(
                 '--num-alerts-clusters',
                 type=int,
                 default=4,
                 help='Number of clusters built from the alerts. '
                      'Default: 4.')

    @staticmethod
    def from_args(args, logger):
        classifier_conf = None
        clustering_conf = None
        if args.alerts_classif is not None:
            multiclass = True
            num_folds = None
            if hasattr(args, 'num_folds'):
                num_folds = args.num_folds
            n_jobs = None
            if hasattr(args, 'n_jobs'):
                n_jobs = args.n_jobs
            factory = classifiers.get_factory()
            classifier_conf = factory.get_default(args.alerts_classif,
                                                  num_folds, n_jobs,
                                                  multiclass, logger)
        elif args.alerts_clustering is not None:
            factory = cluster_conf.get_factory()
            clustering = factory.get_class(args.alerts_clustering)
            clustering_conf = clustering(logger, args.num_alerts_clusters)
        return AlertsConf(args.detection_threshold, classifier_conf,
                          clustering_conf, logger)
