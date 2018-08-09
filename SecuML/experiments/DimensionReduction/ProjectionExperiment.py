# SecuML
# Copyright (C) 2017-2018  ANSSI
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

from SecuML.core.DimensionReduction.Configuration import DimensionReductionConfFactory

from SecuML.experiments import ExperimentFactory
from SecuML.experiments.DimensionReduction.DimensionReductionExperiment import DimensionReductionExperiment


class ProjectionExperiment(DimensionReductionExperiment):

    def getKind(self):
        return 'Projection'

    def generateSuffix(self):
        suffix = ''
        suffix += self.conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj, session):
        conf = DimensionReductionConfFactory.getFactory().fromJson(obj['conf'])
        experiment = ProjectionExperiment(obj['project'], obj['dataset'],
                                          session, create=False)
        DimensionReductionExperiment.expParamFromJson(experiment, obj, conf)
        return experiment

    def toJson(self):
        conf = DimensionReductionExperiment.toJson(self)
        conf['__type__'] = 'ProjectionExperiment'
        conf['conf'] = self.conf.toJson()
        return conf

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(
            description='Projection of the data for data visualization.')
        DimensionReductionExperiment.projectDatasetFeturesParser(parser)
        DimensionReductionExperiment.generateDimensionReductionParser(parser)
        algos = ['Pca', 'Rca', 'Lda', 'Lmnn', 'Nca', 'Itml']
        subparsers = parser.add_subparsers(dest='algo')
        factory = DimensionReductionConfFactory.getFactory()
        for algo in algos:
            algo_parser = subparsers.add_parser(algo)
            factory.generateParser(algo, algo_parser)
        return parser

    def webTemplate(self):
        return 'DimensionReduction/projection.html'


ExperimentFactory.getFactory().registerClass('ProjectionExperiment',
                                             ProjectionExperiment)
