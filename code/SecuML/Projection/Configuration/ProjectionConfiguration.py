## SecuML
## Copyright (C) 2016  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

from SecuML.Experiment.Experiment import Experiment

class ProjectionConfiguration(object):

    def __init__(self, algo, num_components = None):
        self.algo           = algo
        self.num_components = num_components

    def generateSuffix(self):
        suffix  = '__' + self.algo.__name__
        return suffix

    def toJson(self):
        conf = {}
        conf['__type__'] = 'ProjectionConfiguration'
        conf['num_components'] = self.num_components
        return conf

    @staticmethod
    def generateParser(parser):
        Experiment.projectDatasetFeturesParser(parser)

        parser.add_argument('--families-supervision',
                action = 'store_true',
                default = False,
                help = 'When set to True, the semi-supervision is based on the families ' +
                'instead of the binary labels. Useless if an unsupervised projection method is used.')

        parser.add_argument('--labels', '-l',
                dest = 'labels_file',
                default = None,
                help = 'CSV file containing the labels of some instances. ' +
                'These labels are used for semi-supervised projections.')

        parser.add_argument('--num-components',
                type = int,
                default = None)

    @staticmethod
    def generateParamsFromArgs(args):
        params = {}
        params['families_supervision'] = args.families_supervision
        params['num_components']       = args.num_components
        return params

