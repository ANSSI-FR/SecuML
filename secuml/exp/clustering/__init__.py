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

from secuml.core.clustering.clusters import Clusters
from secuml.core.projection.algos.semi_supervised import FewerThanTwoLabels
from secuml.exp.conf.features import FeaturesConf
from secuml.exp.projection import ProjectionExperiment
from secuml.exp.projection.conf import ProjectionConf
from secuml.exp.experiment import Experiment
from secuml.exp import experiment
from .conf import ClusteringConf


class ClusteringExperiment(Experiment):

    def create_exp(self):
        Experiment.create_exp(self)
        # create projection experiment
        self.projection_exp = None
        if self.exp_conf.core_conf is None:
            return
        projection_core_conf = self.exp_conf.core_conf.projection_conf
        if projection_core_conf is not None:
            features_conf = FeaturesConf(
                    self.exp_conf.features_conf.input_features,
                    self.exp_conf.secuml_conf.logger)
            projection_conf = ProjectionConf(
                                self.exp_conf.secuml_conf,
                                self.exp_conf.dataset_conf,
                                features_conf,
                                self.exp_conf.annotations_conf,
                                projection_core_conf,
                                name='-'.join([self.exp_conf.name, 'proj']),
                                parent=self.exp_id)
            self.projection_exp = ProjectionExperiment(projection_conf,
                                                       session=self.session)

    def get_instances(self, instances=None):
        instances = Experiment.get_instances(self, instances=instances)
        if self.exp_conf.label != 'all':
            selected_ids = instances.ground_truth.get_annotated_ids(
                                                    label=self.exp_conf.label)
            instances = instances.get_from_ids(selected_ids)
        if self.projection_exp is not None:
            try:
                instances = self.projection_exp.run(instances=instances,
                                                    export=False)
            except FewerThanTwoLabels:
                self.conf.logger.warning('There are too few class labels.'
                                         'The instances are not projected '
                                         'before building the clustering.')
        return instances

    def run(self, instances=None, drop_annotated_instances=False, quick=False):
        Experiment.run(self)
        instances = self.get_instances()
        core_conf = self.exp_conf.core_conf
        clustering = core_conf.algo(instances, core_conf)
        clustering.fit()
        clustering.generate(drop_annotated_instances=drop_annotated_instances)
        clustering.export(self.output_dir(), quick=quick)

    def set_clusters(self, instances, assigned_clusters, assignment_proba,
                     centroids, drop_annotated_instances, cluster_labels):
        Experiment.run(self)
        clustering = Clusters(instances, assigned_clusters)
        clustering.generate(assignment_proba, centroids,
                            drop_annotated_instances=drop_annotated_instances,
                            cluster_labels=cluster_labels)
        clustering.export(self.output_dir(),
                          drop_annotated_instances=drop_annotated_instances)

    def web_template(self):
        return 'clustering/main.html'


experiment.get_factory().register('Clustering', ClusteringExperiment,
                                  ClusteringConf)
