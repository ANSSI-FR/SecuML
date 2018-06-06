# SecuML
# Copyright (C) 2016  ANSSI
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

from SecuML.core.Configuration import Configuration
from SecuML.core.DimensionReduction.Configuration import DimensionReductionConfFactory

from . import ClusteringConfFactory


class ClusteringConfiguration(object):

    def __init__(self, num_clusters, num_results=None, projection_conf=None,
                 label='all', logger=None):
        Configuration.__init__(self, logger=logger)
        self.num_clusters = num_clusters
        if num_results is not None:
            self.num_results = num_results
        else:
            self.num_results = 10
        self.projection_conf = projection_conf
        self.label = label
        self.algo = None

    def setDimensionReductionConf(self, projection_conf):
        self.projection_conf = projection_conf

    def setNumClusters(self, num_clusters):
        self.num_clusters = num_clusters

    def generateSuffix(self):
        suffix = '__' + str(self.num_clusters)
        suffix += '_' + self.algo.__name__
        if self.projection_conf is not None:
            suffix += self.projection_conf.generateSuffix()
        if self.label != 'all':
            suffix += '__' + self.label
        return suffix

    @staticmethod
    def fromJson(obj):
        conf = ClusteringConfiguration(
            obj['num_clusters'], num_results=obj['num_results'], label=obj['label'])
        if obj['projection_conf'] is not None:
            projection_conf = DimensionReductionConfFactory.getFactory(
            ).fromJson(obj['projection_conf'])
            conf.setDimensionReductionConf(projection_conf)
        return conf

    def toJson(self):
        conf = {}
        conf['__type__'] = 'ClusteringConfiguration'
        conf['num_clusters'] = self.num_clusters
        conf['num_results'] = self.num_results
        conf['projection_conf'] = None
        if self.projection_conf is not None:
            conf['projection_conf'] = self.projection_conf.toJson()
        conf['label'] = self.label
        conf['algo'] = self.algo
        if self.algo is not None:
            conf['algo'] = self.algo.__name__
        return conf

    @staticmethod
    def generateParser(parser):
        # Clustering arguments
        parser.add_argument('--num-clusters',
                            type=int,
                            default=4)
        label_help = 'The clustering is built from all the instances in the dataset, '
        label_help += 'or only from the benign or malicious ones. '
        label_help += 'By default, the clustering is built from all the instances. '
        label_help += 'The malicious and benign instances are selected according to '
        label_help += 'the ground-truth stored in annotations/ground_truth.csv.'
        parser.add_argument('--label',
                            choices=['all', 'malicious', 'benign'],
                            default='all',
                            help=label_help)
        # DimensionReduction arguments
        projection_group = parser.add_argument_group(
            'DimensionReduction parameters')
        projection_group.add_argument('--projection-algo',
                                      choices=['Pca', 'Rca', 'Lda',
                                               'Lmnn', 'Nca', 'Itml', None],
                                      default=None,
                                      help='DimensionReduction performed before building the clustering. ' +
                                      'By default the instances are not projected.')
        projection_group.add_argument('--families-supervision',
                                      action='store_true',
                                      default=False,
                                      help='When set to True, the semi-supervision is based on the families ' +
                                      'instead of the binary labels. Useless if an unsupervised projection method is used.')
        projection_group.add_argument('--annotations', '-a',
                                      dest='annotations_file',
                                      default=None,
                                      help='CSV file containing the annotations of some instances. ' +
                                      'These annotations are used for semi-supervised projections.')

    @staticmethod
    def generateParamsFromArgs(args):

        # DimensionReduction parameters
        projection_conf = None
        if args.projection_algo is not None:
            projection_args = {}
            projection_args['families_supervision'] = args.families_supervision
            projection_args['num_components'] = None
            projection_conf = DimensionReductionConfFactory.getFactory().fromParam(
                args.projection_algo, projection_args)

        # Clustering parameters
        params = {}
        params['num_clusters'] = args.num_clusters
        params['num_results'] = 5
        params['projection_conf'] = projection_conf
        params['label'] = args.label

        return params


ClusteringConfFactory.getFactory().registerClass('ClusteringConfiguration',
                                                 ClusteringConfiguration)
