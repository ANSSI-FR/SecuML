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

import argparse

from SecuML.core.Data.DescriptiveStatistics import DescriptiveStatistics

from SecuML.experiments import ExperimentFactory
from SecuML.experiments.Experiment import Experiment
from SecuML.experiments.InstancesFromExperiment import InstancesFromExperiment


class DescriptiveStatisticsExperiment(Experiment):

    def getKind(self):
        return 'DescriptiveStatistics'

    def generateSuffix(self):
        return ''

    def run(self):
        instances = InstancesFromExperiment(self).getInstances()
        stats = DescriptiveStatistics()
        stats.generateDescriptiveStatistics(
            instances, self.getOutputDirectory())

    @staticmethod
    def fromJson(obj, session):
        experiment = DescriptiveStatisticsExperiment(obj['project'], obj['dataset'],
                                                     session, create=False)
        Experiment.expParamFromJson(experiment, obj, None)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'DescriptiveStatisticsExperiment'
        return conf

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(
            description='Descriptive Statistics of the Dataset')
        Experiment.projectDatasetFeturesParser(parser)
        return parser

    def webTemplate(self):
        return 'DescriptiveStatistics/descriptive_statistics.html'

    def setExperimentFromArgs(self, args):
        self.setConf(None, args.features_file,
                     annotations_filename='ground_truth.csv')
        self.export()


ExperimentFactory.getFactory().registerClass('DescriptiveStatisticsExperiment',
                                             DescriptiveStatisticsExperiment)
