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

import abc
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from secuml.core.clustering.clusters import Clusters


class ClusteringAlgorithm(object):

    def __init__(self, instances, conf):
        self.instances = instances
        self.conf = conf
        self.num_clusters = self.conf.num_clusters
        self.clustering = None

    @abc.abstractmethod
    def get_distortion(self):
        return

    @abc.abstractmethod
    def get_centroids(self):
        return

    @abc.abstractmethod
    def get_assigned_clusters(self):
        return

    def get_predicted_proba(self):
        return None

    def get_all_proba(self):
        return None

    def fit(self):
        self.pipeline = Pipeline([('scaler', StandardScaler()),
                                  ('clustering', self.algo)])
        self.pipeline.fit(self.instances.features.get_values())

    def generate(self, drop_annotated_instances=False):
        self.clustering = Clusters(self.instances, self.get_assigned_clusters(),
                                   clustering_algo=self)
        self.clustering.generate(
                self.get_all_proba(),
                self.get_centroids(),
                drop_annotated_instances=drop_annotated_instances)

    def export(self, output_dir, quick=False):
        self.clustering.export(output_dir)
        self.clustering.gen_eval(output_dir, quick=quick)
