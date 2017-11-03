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

from SecuML.Clustering.Configuration.ClusteringConfiguration import ClusteringConfiguration
from SecuML.Clustering.Clustering import Clustering

from SecuML.Experiment.ClassificationExperiment import ClassificationExperiment
from SecuML.Experiment.ClusteringExperiment import ClusteringExperiment

from CategoriesExp import CategoriesExp
from RareCategoryDetectionAnnotationQueries import RareCategoryDetectionAnnotationQueries

class RareCategoryDetectionAnnotationQueriesExp(RareCategoryDetectionAnnotationQueries):

    def __init__(self, iteration, label, proba_min, proba_max,
            multiclass_model = None,
            multiclass_exp = None):
        RareCategoryDetectionAnnotationQueries.__init__(self, iteration, label, proba_min, proba_max,
                multiclass_model = None)
        self.multiclass_exp = multiclass_exp
        self.experiment = iteration.experiment

    def getMulticlassConf(self):
        conf = self.rare_category_detection_conf.classification_conf
        exp  = self.experiment
        name = '-'.join(['AL' + str(exp.experiment_id),
                         'Iter' + str(self.iteration.iteration_number),
                         self.label,
                         'analysis'])
        self.multiclass_exp = ClassificationExperiment(exp.project, exp.dataset,
                                                  exp.session,
                                                  experiment_name = name,
                                                  labels_id = exp.labels_id,
                                                  parent = exp.experiment_id)
        self.multiclass_exp.setFeaturesFilenames(exp.features_filenames)
        self.multiclass_exp.setClassifierConf(conf)
        self.multiclass_exp.createExperiment()
        self.multiclass_exp.export()
        return conf

    def createClusteringExperiment(self):
        conf = ClusteringConfiguration(self.categories.numCategories())
        exp  = self.experiment
        name = '-'.join(['AL' + str(exp.experiment_id),
                         'Iter' + str(self.iteration.iteration_number),
                         self.label,
                         'clustering'])
        clustering_exp = ClusteringExperiment(exp.project, exp.dataset, exp.session,
                                              conf,
                                              labels_id = exp.labels_id,
                                              experiment_name = name,
                                              parent = exp.experiment_id)
        clustering_exp.setFeaturesFilenames(exp.features_filenames)
        clustering_exp.createExperiment()
        clustering_exp.export()
        return clustering_exp

    def generateClusteringVisualization(self):
        if self.families_analysis:
            self.clustering_exp = self.createClusteringExperiment()
            clustering = Clustering(self.categories.instances,
                                    self.categories.assigned_categories)
            clustering.generateClustering(None, None)
            clustering.export(self.clustering_exp.getOutputDirectory())
        else:
            self.clustering_exp = None

    def setCategories(self, all_instances, assigned_categories, predicted_proba):
        self.categories = CategoriesExp(self.multiclass_exp,
                                        self.iteration,
                                        all_instances,
                                        assigned_categories,
                                        predicted_proba,
                                        self.label,
                                        self.multiclass_model.class_labels)
