# SecuML
# Copyright (C) 2016-2018  ANSSI
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

from SecuML.core.active_learning.strategies.queries.RareCategoryDetectionQueries \
    import RareCategoryDetectionQueries
from SecuML.core.clustering.conf.ClusteringConf \
        import ClusteringConf as CoreClusteringConf
from SecuML.core.clustering.Clustering import Clustering

from SecuML.exp.active_learning.strategies.queries.QueryExp import QueryExp
from SecuML.exp.active_learning.strategies.queries.CategoriesExp \
        import CategoriesExp
from SecuML.exp.classification.ClassificationConf \
        import ClassificationConf
from SecuML.exp.classification.ClassificationExperiment \
        import ClassificationExperiment
from SecuML.exp.clustering.ClusteringConf \
        import ClusteringConf
from SecuML.exp.clustering.ClusteringExperiment \
        import ClusteringExperiment


class RareCategoryDetectionQueriesExp(RareCategoryDetectionQueries):

    def __init__(self, iteration, label, proba_min, proba_max,
                 multiclass_exp=None, input_checking=True):
        RareCategoryDetectionQueries.__init__(self, iteration, label, proba_min,
                                              proba_max,
                                              input_checking=input_checking)
        self.multiclass_exp = multiclass_exp
        self.experiment = iteration.experiment

    def generateQuery(self, instance_id, predicted_proba,
                                suggested_label, suggested_family,
                                confidence=None):
        return QueryExp(instance_id, predicted_proba, suggested_label,
                        suggested_family, confidence=confidence)

    def getMulticlassConf(self):
        conf = self.rcd_conf.classification_conf
        exp = self.experiment
        name = '-'.join(['AL%d' % exp.experiment_id,
                         'Iter%d' % self.iteration.iteration_number,
                         self.label,
                         'analysis'])
        exp_conf = ClassificationConf(exp.exp_conf.secuml_conf,
                                      exp.exp_conf.dataset_conf,
                                      exp.exp_conf.features_conf,
                                      exp.exp_conf.annotations_conf,
                                      conf,
                                      experiment_name=name,
                                      parent=exp.experiment_id)
        self.multiclass_exp = ClassificationExperiment(exp_conf,
                                                       session=exp.session)
        self.multiclass_exp.create_exp()
        return conf

    def createClusteringExperiment(self):
        exp = self.experiment
        core_conf = CoreClusteringConf(exp.exp_conf.logger,
                                       self.categories.numCategories())
        name = '-'.join(['AL%d' % exp.experiment_id,
                         'Iter%d' % self.iteration.iteration_number,
                         self.label,
                         'clustering'])
        exp_conf = ClusteringConf(exp.exp_conf.secuml_conf,
                                  exp.exp_conf.dataset_conf,
                                  exp.exp_conf.features_conf,
                                  exp.exp_conf.annotations_conf,
                                  core_conf,
                                  experiment_name=name,
                                  parent=exp.experiment_id)
        clustering_exp = ClusteringExperiment(exp_conf, session=exp.session)
        clustering_exp.create_exp()
        return clustering_exp

    def generateClusteringVisualization(self):
        if self.families_analysis:
            self.clustering_exp = self.createClusteringExperiment()
            clustering = Clustering(self.categories.instances,
                                    self.categories.assigned_categories)
            clustering.generateClustering(None, None)
            clustering.export(self.clustering_exp.output_dir())
        else:
            self.clustering_exp = None

    def setCategories(self, all_instances, assigned_categories,
                      predicted_proba):
        self.categories = CategoriesExp(self.multiclass_exp,
                                        self.iteration,
                                        all_instances,
                                        assigned_categories,
                                        predicted_proba,
                                        self.label,
                                        self.multiclass_model.class_labels)
