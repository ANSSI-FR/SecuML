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

from __future__ import division

import abc
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import warnings

from Clustering import Clustering
from SecuML.Experiment.ProjectionExperiment import ProjectionExperiment
from SecuML.Projection.Algorithms.SemiSupervisedProjection import FewerThanTwoLabels

class ClusteringAlgorithm(object):

    def __init__(self, instances, experiment):
        self.instances    = instances
        self.experiment   = experiment
        self.num_clusters = experiment.conf.num_clusters
        self.clustering   = None

    @abc.abstractmethod
    def getDistortion(self):
        return

    @abc.abstractmethod
    def getCentroids(self):
        return

    @abc.abstractmethod
    def getAssignedClusters(self):
        return

    def getPredictedProba(self):
        return None

    def getAllProba(self):
        return None

    def run(self, quick = False, drop_annotated_instances = False):
        if self.experiment.conf.projection_conf is not None:
            try:
                self.projectInstances(quick)
            except FewerThanTwoLabels:
                warnings.warn('There are too few class labels.'
                              'The instances are not projected before building the clustering.')
        self.compute()
        self.clustering = Clustering(self.experiment, self.instances, self.getAssignedClusters(),
                clustering_algo = self)
        self.clustering.generateClustering(self.getAllProba(),
                                           self.getCentroids(),
                                           drop_annotated_instances = drop_annotated_instances)
        self.clustering.generateEvaluation(quick = quick)

    def projectInstances(self, quick):
        projection_exp = self.createProjectionExperiment()
        algo = projection_exp.conf.algo
        projection = algo(projection_exp)
        instances = projection.getFittingInstances(self.instances)
        projection.fit(instances, visu = not quick)
        self.instances = projection.transform(self.instances, visu = not quick, performance = not quick)

    def compute(self):
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('clustering', self.algo)])
        self.pipeline.fit(self.instances.getFeatures())

    def createProjectionExperiment(self):
        exp = self.experiment
        name = '-'.join([exp.experiment_name, 'projection'])
        projection_conf = exp.conf.projection_conf
        projection_exp = ProjectionExperiment(
                exp.project, exp.dataset, exp.db, exp.cursor,
                experiment_name = name,
                experiment_label = exp.experiment_label,
                parent = exp.experiment_id)
        projection_exp.setConf(projection_conf)
        projection_exp.setFeaturesFilenames(exp.features_filenames)
        projection_exp.createExperiment()
        projection_exp.export()
        return projection_exp
