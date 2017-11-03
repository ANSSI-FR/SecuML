## SecuML
## Copyright (C) 2017  ANSSI
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

import argparse

from SecuML.DimensionReduction.Configuration import DimensionReductionConfFactory

import ExperimentFactory
from DimensionReductionExperiment import DimensionReductionExperiment

class FeatureSelectionExperiment(DimensionReductionExperiment):

    def __init__(self, project, dataset, session, experiment_name = None,
                 labels_id = None, parent = None):
        DimensionReductionExperiment.__init__(self, project, dataset, session,
                            experiment_name = experiment_name,
                            labels_id = labels_id,
                            parent = parent)
        self.kind = 'FeatureSelection'

    def setConf(self, conf):
        self.conf = conf

    def generateSuffix(self):
        suffix  = ''
        suffix += self.conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj, session):
        conf = DimensionReductionConfFactory.getFactory().fromJson(obj['conf'])
        experiment = FeatureSelectionExperiment(obj['project'], obj['dataset'],
                                                session)
        DimensionReductionExperiment.expParamFromJson(experiment, obj)
        experiment.setConf(conf)
        return experiment

    def toJson(self):
        conf = DimensionReductionExperiment.toJson(self)
        conf['__type__'] = 'FeatureSelectionExperiment'
        conf['conf'] = self.conf.toJson()
        return conf

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(
                description = 'Feature Selection.')
        algos = ['ChiSquare', 'Fclassif', 'MutualInfoClassif', 'VarianceFilter',
                 'RecursiveFeatureElimination', 'NoneFilter']
        DimensionReductionExperiment.projectDatasetFeturesParser(parser)
        DimensionReductionExperiment.generateDimensionReductionParser(parser)
        subparsers = parser.add_subparsers(dest = 'algo')
        factory = DimensionReductionConfFactory.getFactory()
        for algo in algos:
            algo_parser = subparsers.add_parser(algo)
            factory.generateParser(algo, algo_parser)
        return parser

    def webTemplate(self):
        return 'DimensionReduction/feature_selection.html'

    def setExperimentFromArgs(self, args):
        self.setFeaturesFilenames(args.features_files)
        factory = DimensionReductionConfFactory.getFactory()
        conf = factory.fromArgs(args.algo, args)
        self.setConf(conf)
        self.initLabels(args.labels_file)
        self.export()

ExperimentFactory.getFactory().registerClass('FeatureSelectionExperiment',
                                             FeatureSelectionExperiment)
