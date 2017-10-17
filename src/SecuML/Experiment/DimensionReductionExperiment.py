## SecuML
## Copyright (C) 2016-2017  ANSSI
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

from SecuML.DimensionReduction.Configuration import DimensionReductionConfFactory

from Experiment import Experiment
from InstancesFromExperiment import InstancesFromExperiment

class DimensionReductionExperiment(Experiment):

    def __init__(self, project, dataset, session, experiment_name = None,
                 labels_id = None, parent = None):
        Experiment.__init__(self, project, dataset, session,
                            experiment_name = experiment_name,
                            labels_id = labels_id,
                            parent = parent)
        self.kind = 'DimensionReduction'

    def setConf(self, conf):
        self.conf = conf

    def generateSuffix(self):
        suffix  = ''
        suffix += self.conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj, session):
        conf = DimensionReductionConfFactory.getFactory().fromJson(obj['conf'])
        experiment = DimensionReductionExperiment(obj['project'], obj['dataset'],
                                                  session)
        Experiment.expParamFromJson(experiment, obj)
        experiment.setConf(conf)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'DimensionReductionExperiment'
        conf['conf'] = self.conf.toJson()
        return conf

    def run(self, instances = None, export = True):
        dimension_reduction = self.conf.algo(self.conf)
        if instances is None:
            instances = InstancesFromExperiment(self).getInstances()
        # Fit
        dimension_reduction.fit(instances)
        if export:
            dimension_reduction.exportFit(self, instances)
        # Transformation
        projected_instances = dimension_reduction.transform(instances)
        if export:
            dimension_reduction.exportTransform(self, instances, projected_instances)
        return projected_instances

    @staticmethod
    def generateDimensionReductionParser(parser):
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
