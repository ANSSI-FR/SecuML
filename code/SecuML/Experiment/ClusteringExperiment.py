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

import argparse
import warnings

from SecuML.Clustering.Configuration import ClusteringConfFactory
from SecuML.DimensionReduction.Algorithms.Projection.SemiSupervisedProjection import FewerThanTwoLabels

import ExperimentFactory
from DimensionReductionExperiment import DimensionReductionExperiment
from Experiment import Experiment
from InstancesFromExperiment import InstancesFromExperiment

class ClusteringExperiment(Experiment):

    def __init__(self, project, dataset, session, conf, experiment_name = None,
                 labels_id = None, parent = None):
        Experiment.__init__(self, project, dataset, session,
                            experiment_name = experiment_name,
                            labels_id = labels_id,
                            parent = parent)
        self.kind = 'Clustering'
        self.conf = conf

    def run(self, instances, label, quick = False, drop_annotated_instances = False):
        if instances is None:
            instances = InstancesFromExperiment(self).getInstances()
        if label != 'all':
            if label == 'malicious':
                selected_ids = instances.getMaliciousIds(true_labels = True)
            elif label == 'benign':
                selected_ids = instances.getBenignIds(true_labels = True)
            instances = instances.getInstancesFromIds(selected_ids)
        clustering = self.conf.algo(instances, self.conf)
        if self.conf.projection_conf is not None:
            try:
                self.projectInstances(instances)
            except FewerThanTwoLabels:
                warnings.warn('There are too few class labels.'
                              'The instances are not projected before building the clustering.')
        clustering.fit()
        clustering.export(self.getOutputDirectory(), quick = quick,
                          drop_annotated_instances = drop_annotated_instances)

    def generateSuffix(self):
        suffix  = ''
        suffix += self.conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj, session):
        conf = ClusteringConfFactory.getFactory().fromJson(obj['conf'])
        experiment = ClusteringExperiment(
                obj['project'], obj['dataset'], session,
                conf)
        Experiment.expParamFromJson(experiment, obj)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ClusteringExperiment'
        conf['conf'] = self.conf.toJson()
        return conf

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(
                description = 'Clustering of the data for data exploration.')
        Experiment.projectDatasetFeturesParser(parser)
        algos = ['Kmeans', 'GaussianMixture']
        subparsers = parser.add_subparsers(dest = 'algo')
        factory = ClusteringConfFactory.getFactory()
        for algo in algos:
            algo_parser = subparsers.add_parser(algo)
            factory.generateParser(algo, algo_parser)
        return parser

    def webTemplate(self):
        return 'Clustering/clustering.html'

    def setExperimentFromArgs(self, args):
        factory = ClusteringConfFactory.getFactory()
        clustering_conf = factory.fromArgs(args.algo, args)
        self.conf = clustering_conf
        self.setFeaturesFilenames(args.features_files)
        self.initLabels(args.labels_file)
        self.export()

    def createDimensionReductionExperiment(self, num_features):
        name = '-'.join([self.experiment_name, 'projection'])
        projection_conf = self.conf.projection_conf
        if projection_conf.num_components is not None:
            if projection_conf.num_components > num_features:
                projection_conf.num_components = num_features
        projection_exp = DimensionReductionExperiment(self.project, self.dataset,
                                              self.session,
                                              experiment_name = name,
                                              labels_id = self.labels_id,
                                              parent = self.experiment_id)
        projection_exp.setConf(projection_conf)
        projection_exp.setFeaturesFilenames(self.features_filenames)
        projection_exp.createExperiment()
        projection_exp.export()
        return projection_exp

    def projectInstances(self, instances):
        projection_exp = self.createDimensionReductionExperiment(instances.numFeatures())
        projected_instances = projection_exp.run(instances = instances, export = False)
        return projected_instances

ExperimentFactory.getFactory().registerClass('ClusteringExperiment',
                                             ClusteringExperiment)
