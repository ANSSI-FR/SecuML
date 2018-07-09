# SecuML
# Copyright (C) 2016-2017  ANSSI
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

from SecuML.core.DimensionReduction.Configuration import DimensionReductionConfFactory

from SecuML.experiments.Experiment import Experiment
from SecuML.experiments.InstancesFromExperiment import InstancesFromExperiment


class DimensionReductionExperiment(Experiment):

    def generateSuffix(self):
        suffix = ''
        suffix += self.conf.generateSuffix()
        return suffix

    def run(self, instances=None, export=True):
        dimension_reduction = self.conf.algo(self.conf)
        if instances is None:
            instances = InstancesFromExperiment(self).getInstances()
        # Fit
        dimension_reduction.fit(instances)
        if export:
            dimension_reduction.exportFit(self.getOutputDirectory(), instances)
        # Transformation
        projected_instances = dimension_reduction.transform(instances)
        if export:
            dimension_reduction.exportTransform(
                self.getOutputDirectory(), instances, projected_instances)
        return projected_instances

    @staticmethod
    def generateDimensionReductionParser(parser):
        parser.add_argument('--families-supervision',
                            action='store_true',
                            default=False,
                            help='When set to True, the semi-supervision is based on the families ' +
                            'instead of the binary labels. Useless if an unsupervised projection method is used.')
        parser.add_argument('--annotations', '-a',
                            dest='annotations_file',
                            default=None,
                            help='CSV file containing the annotations of some instances. ' +
                            'These annotations are used for semi-supervised projections.')

    def setExperimentFromArgs(self, args):
        factory = DimensionReductionConfFactory.getFactory()
        conf = factory.fromArgs(args.algo, args, logger=self.logger)
        self.setConf(conf, args.features_file,
                     annotations_filename=args.annotations_file)
        self.export()
