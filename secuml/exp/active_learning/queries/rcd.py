# SecuML
# Copyright (C) 2016-2019  ANSSI
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

from secuml.core.active_learning.queries.rcd import RcdQueries \
        as CoreRcdQueries
from secuml.core.clustering.conf.algos import ClusteringConf \
        as CoreClusteringConf
from secuml.core.clustering.clusters import Clusters

from secuml.exp.clustering.conf import ClusteringConf
from secuml.exp.clustering import ClusteringExperiment
from secuml.exp.conf.features import FeaturesConf
from secuml.exp.diadem.conf.diadem import DiademConf
from secuml.exp.diadem import DiademExp
from . import Query
from .categories import Categories


class RcdQueries(CoreRcdQueries):

    def __init__(self, iteration, label, proba_min=None, proba_max=None,
                 input_checking=True):
        CoreRcdQueries.__init__(self, iteration, label, proba_min, proba_max,
                                input_checking=input_checking)
        self.multiclass_exp = None
        self.exp = iteration.exp

    def generate_query(self, instance_id, predicted_proba, suggested_label,
                       suggested_family, confidence=None):
        return Query(instance_id, predicted_proba, suggested_label,
                     suggested_family, confidence=confidence)

    def _get_multiclass_conf(self):
        conf = self.rcd_conf.classification_conf
        name = '-'.join(['AL%d' % self.exp.exp_id,
                         'Iter%d' % self.iteration.iter_num,
                         self.label,
                         'analysis'])
        features_conf = FeaturesConf(
                self.exp.exp_conf.features_conf.input_features,
                self.exp.exp_conf.features_conf.sparse,
                self.exp.exp_conf.features_conf.logger,
                filter_in_f=self.exp.exp_conf.features_conf.filter_in_f,
                filter_out_f=self.exp.exp_conf.features_conf.filter_out_f)
        exp_conf = DiademConf(self.exp.exp_conf.secuml_conf,
                              self.exp.exp_conf.dataset_conf,
                              features_conf,
                              self.exp.exp_conf.annotations_conf,
                              conf, None, name=name, parent=self.exp.exp_id)
        self.multiclass_exp = DiademExp(exp_conf, session=self.exp.session)
        return conf

    def _create_clustering_exp(self):
        core_conf = CoreClusteringConf(self.exp.exp_conf.logger,
                                       self.categories.num_categories)
        name = '-'.join(['AL%d' % self.exp.exp_id,
                         'Iter%d' % self.iteration.iter_num,
                         self.label,
                         'clustering'])
        features_conf = FeaturesConf(
                self.exp.exp_conf.features_conf.input_features,
                self.exp.exp_conf.features_conf.sparse,
                self.exp.exp_conf.features_conf.logger,
                filter_in_f=self.exp.exp_conf.features_conf.filter_in_f,
                filter_out_f=self.exp.exp_conf.features_conf.filter_out_f)
        exp_conf = ClusteringConf(self.exp.exp_conf.secuml_conf,
                                  self.exp.exp_conf.dataset_conf,
                                  features_conf,
                                  self.exp.exp_conf.annotations_conf,
                                  core_conf, name=name, parent=self.exp.exp_id)
        clustering_exp = ClusteringExperiment(exp_conf,
                                              session=self.exp.session)
        return clustering_exp

    def _gen_clustering_visu(self):
        if self.families_analysis:
            self.clustering_exp = self._create_clustering_exp()
            clustering = Clusters(self.categories.instances,
                                  self.categories.assigned_categories)
            clustering.generate(None, None)
            clustering.export(self.clustering_exp.output_dir())
        else:
            self.clustering_exp = None

    def _set_categories(self, all_instances, assigned_categories,
                        predicted_proba):
        self.categories = Categories(self.multiclass_exp, self.iteration,
                                     all_instances, assigned_categories,
                                     predicted_proba, self.label,
                                     self.multiclass_model.class_labels)
