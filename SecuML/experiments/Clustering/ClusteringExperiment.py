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

from SecuML.core.Clustering.Configuration import ClusteringConfFactory
from SecuML.core.DimensionReduction.Algorithms.Projection.SemiSupervisedProjection \
        import FewerThanTwoLabels

from SecuML.experiments import ExperimentFactory
from SecuML.experiments.Data.InstancesFromExperiment \
        import InstancesFromExperiment
from SecuML.experiments.DimensionReduction.ProjectionExperiment \
        import ProjectionExperiment
from SecuML.experiments.Experiment import Experiment


class ClusteringExperiment(Experiment):

    def getKind(self):
        return 'Clustering'

    def run(self, instances, label, quick=False,
            drop_annotated_instances=False):
        if instances is None:
            instances = InstancesFromExperiment(self).getInstances()
        if label != 'all':
            selected_ids = instances.ground_truth.getAnnotatedIds(label=label)
            instances = instances.getInstancesFromIds(selected_ids)
        clustering = self.conf.algo(instances, self.conf)
        if self.conf.projection_conf is not None:
            try:
                self.projectInstances(instances)
            except FewerThanTwoLabels:
                self.conf.logger.warning('There are too few class labels.'
                                         'The instances are not projected '
                                         'before building the clustering.')
        clustering.fit()
        clustering.generateClustering(
            drop_annotated_instances=drop_annotated_instances)
        clustering.export(self.getOutputDirectory(), quick=quick,
                          drop_annotated_instances=drop_annotated_instances)

    def generateSuffix(self):
        suffix = ''
        suffix += self.conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj, secuml_conf):
        conf = ClusteringConfFactory.getFactory().fromJson(obj['conf'])
        experiment = ClusteringExperiment(secuml_conf)
        experiment.initExperiment(obj['project'], obj['dataset'],
                                  create=False)
        Experiment.expParamFromJson(experiment, obj, conf)
        return experiment

    def toJson(self):
        conf = Experiment.toJson(self)
        conf['__type__'] = 'ClusteringExperiment'
        conf['conf'] = self.conf.toJson()
        return conf

    @staticmethod
    def generateParser():
        parser = argparse.ArgumentParser(
            description='Clustering of the data for data exploration.')
        Experiment.projectDatasetFeturesParser(parser)
        subparsers = parser.add_subparsers(dest='algo')
        subparsers.required = True
        factory = ClusteringConfFactory.getFactory()
        algos = factory.getAlgorithms()
        for algo in algos:
            algo_parser = subparsers.add_parser(algo)
            factory.generateParser(algo, algo_parser)
        return parser

    def webTemplate(self):
        return 'Clustering/clustering.html'

    def setExperimentFromArgs(self, args):
        self.initExperiment(args.project, args.dataset,
                            experiment_name=args.exp_name)
        factory = ClusteringConfFactory.getFactory()
        conf = factory.fromArgs(args.algo, args, logger=self.logger)
        self.setConf(conf, args.features_file,
                     annotations_filename=args.annotations_file)
        self.export()

    def createProjectionExperiment(self, num_features):
        name = '-'.join([self.experiment_name, 'projection'])
        projection_conf = self.conf.projection_conf
        if projection_conf.num_components is not None:
            if projection_conf.num_components > num_features:
                projection_conf.num_components = num_features
        projection_exp = ProjectionExperiment(self.secuml_conf,
                                              session=self.session)
        projection_exp.initExperiment(self.project, self.dataset,
                                      experiment_name=name,
                                      parent=self.experiment_id)
        projection_exp.setConf(projection_conf, self.features_filename)
        projection_exp.export()
        return projection_exp

    def projectInstances(self, instances):
        projection_exp = self.createProjectionExperiment(
            instances.numFeatures())
        projected_instances = projection_exp.run(instances=instances,
                                                 export=False)
        return projected_instances


ExperimentFactory.getFactory().registerClass('ClusteringExperiment',
                                             ClusteringExperiment)
