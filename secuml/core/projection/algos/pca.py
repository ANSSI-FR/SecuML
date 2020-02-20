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

import copy
import numpy as np
import pandas as pd
import os.path as path
from sklearn import decomposition

from .unsupervised import UnsupervisedProjection


class Pca(UnsupervisedProjection):

    def __init__(self, conf):
        UnsupervisedProjection.__init__(self, conf)
        self.projection = decomposition.PCA(n_components=conf.num_components)

    def fit(self, instances):
        UnsupervisedProjection.fit(self, instances)

    def transform(self, instances):
        projected_instances = UnsupervisedProjection.transform(self, instances)
        return projected_instances

    def set_projection_matrix(self):
        self.projection_matrix = np.transpose(
            self.pipeline['projection'].components_)

    def get_fitting_instances(self, instances):
        return instances

    def export_fit(self, output_dir, instances):
        UnsupervisedProjection.export_fit(self, output_dir, instances)
        self.export_explained_var(output_dir)
        self.export_cum_explained_var(output_dir)

    def export_transform(self, output_dir, instances, projected_instances):
        UnsupervisedProjection.export_transform(self, output_dir, instances,
                                                projected_instances)
        self.export_reconstruction_errors(output_dir, instances,
                                          projected_instances)

    def export_explained_var(self, directory):
        explained_var = pd.DataFrame(self.projection.explained_variance_ratio_,
                                     index=list(range(self.num_components)),
                                     columns=['y'])
        explained_var.index.name = 'x'
        explained_var.to_csv(path.join(directory,
                                       'explained_variance.csv'),
                             sep=',',
                             header=True,
                             index=True)

    def export_cum_explained_var(self, directory):
        explained_var = pd.DataFrame(
            {'y': np.cumsum(self.projection.explained_variance_ratio_)},
            index=list(range(self.num_components)))
        explained_var.index.name = 'x'
        explained_var.to_csv(path.join(directory,
                                       'cumuled_explained_variance.csv'),
                             sep=',',
                             header=True,
                             index=True)

    def export_reconstruction_errors(self, output_dir, instances,
                                     projected_instances):
        reconstruction_errors = pd.DataFrame(
                                        list(range(self.num_components)),
                                        index=list(range(self.num_components)),
                                        columns=['y'])
        reconstruction_errors.index.name = 'x'
        for c in range(self.num_components):
            reconstruction_error = self.reconstruction_error(
                instances, projected_instances, c + 1)
            reconstruction_errors.at[c, 'y'] = reconstruction_error
        reconstruction_errors.to_csv(path.join(output_dir,
                                               'reconstruction_errors.csv'),
                                     sep=',',
                                     header=True,
                                     index=True)

    def get_reconstructed_data(self, projected_instances, projection_size):
        projection = copy.deepcopy(projected_instances.features.get_values())
        projection = np.array(projection)[:, :projection_size]
        projection_matrix = np.transpose(
            self.projection_matrix[:, list(range(projection_size))])
        reconstructed_data = projection.dot(projection_matrix)
        return reconstructed_data

    def reconstruction_error(self, instances, projected_instances,
                             projection_size):
        reconstructed_data = self.get_reconstructed_data(projected_instances,
                                                         projection_size)
        reconstruction_error = 0
        diff = reconstructed_data - instances.features.get_values()
        for i in range(instances.num_instances()):
            reconstruction_error += np.sum([x * x for x in diff[i, :]])
        reconstruction_error /= instances.num_instances()
        return reconstruction_error
