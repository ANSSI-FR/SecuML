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

import csv
import os
import numpy as np

from SecuML.core.data.Features import Features
from SecuML.core.data.Ids import Ids
from SecuML.exp import db_tables
from SecuML.exp.db_tables import FeaturesFilesAlchemy
from SecuML.exp.db_tables import InstancesAlchemy
from SecuML.exp.conf.FeaturesConf import InputFeaturesTypes


class FeaturesFromExp(Features):

    def __init__(self, exp, instance_ids=None):
        if instance_ids is None:
            dataset_id = exp.exp_conf.dataset_conf.dataset_id
            instance_ids = Ids(db_tables.getDatasetIds(exp.session, dataset_id))
        self._set_exp_conf(exp)
        ids, names, descriptions = self._set_paths_masks_names()
        values = self._get_matrix()
        Features.__init__(self, values, ids, names, descriptions, instance_ids)

    def _set_exp_conf(self, exp):
        self.session = exp.session
        self.dataset_conf = exp.exp_conf.dataset_conf
        self.dataset_id = self.dataset_conf.dataset_id
        self.exp_id = exp.exp_conf.experiment_id
        self.exp_conf = exp.exp_conf
        self.features_conf = self.exp_conf.features_conf

    def _set_paths_masks_names(self):
        ids = []
        names = []
        descriptions = []
        dataset_dir = self.dataset_conf.input_dir(self.exp_conf.secuml_conf)
        dir_ = os.path.join(dataset_dir, 'features')
        if self.features_conf.input_type == InputFeaturesTypes.dir:
            dir_ = os.path.join(dir_, self.features_conf.input_features)
        self.paths_masks = []
        for file_id in self.features_conf.features_files_ids:
            query = self.session.query(FeaturesFilesAlchemy)
            query = query.filter(FeaturesFilesAlchemy.id == file_id)
            row = query.one()
            # file path
            file_path = os.path.join(dir_, row.filename)
            # mask
            if self.features_conf.filter_in is not None:
                mask = [f.user_id in self.features_conf.filter_in
                        for f in row.features]
            elif self.features_conf.filter_out is not None:
                mask = [f.user_id not in self.features_conf.filter_out
                        for f in row.features]
            else:
                mask = [True for _ in range(len(row.features))]
            self.paths_masks.append((file_path, mask))
            # ids, names, descriptions
            ids.extend([f.id for i, f in enumerate(row.features)
                        if mask[i]])
            names.extend([f.name for i, f in enumerate(row.features)
                          if mask[i]])
            descriptions.extend([f.description
                                 for i, f in enumerate(row.features)
                                 if mask[i]])
        return ids, names, descriptions

    def get_instance(self, instance_id):
        query = self.session.query(InstancesAlchemy)
        query = query.filter(InstancesAlchemy.dataset_id == self.dataset_id)
        query = query.filter(InstancesAlchemy.id == instance_id)
        row_number = query.one().row_number
        features_values = []
        for features_file, mask in self.paths_masks:
            line = 1
            with open(features_file, 'r') as f_file:
                next(f_file)  # skip header
                while line < row_number:
                    next(f_file)
                    line = line + 1
                row = next(f_file).rstrip(),
                features_reader = csv.reader(row)
                values = np.array(next(features_reader)[1:])[mask]
                features_values = np.hstack((features_values, values))
        return self.names, features_values

    def _get_matrix(self):
        features = None
        for csv_file, mask in self.paths_masks:
            with open(csv_file, 'r') as f:
                f.readline()
                reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
                matrix = list(list(rec) for rec in reader)
                matrix = np.array([l[1:] for l in matrix])[:, mask]
                if features is None:
                    features = matrix
                else:
                    features = np.hstack((features, matrix))
        return features
