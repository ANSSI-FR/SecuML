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
import pandas as pd
from sqlalchemy.orm.exc import NoResultFound

from . import compute_hash
from secuml.exp.conf.features import InputFeaturesTypes
from secuml.exp.tools.db_tables import DatasetFeaturesAlchemy
from secuml.exp.tools.db_tables import FeaturesFilesAlchemy
from secuml.exp.tools.db_tables import FeaturesAlchemy
from secuml.exp.tools.exp_exceptions import SecuMLexpException
from secuml.exp.tools.exp_exceptions import UpdatedDirectory
from secuml.exp.tools.exp_exceptions import UpdatedFile


class FeaturesNotFound(SecuMLexpException):

    def __init__(self, input_path):
        self.input_path = input_path

    def __str__(self):
        return('Invalid features path: %s does not exist.' % self.input_path)


class LoadFeatures(object):

    def __init__(self, exp_conf, secuml_conf, session):
        self.secuml_conf = secuml_conf
        self.exp_conf = exp_conf
        self.features_conf = exp_conf.features_conf
        self.session = session

    def load(self):
        dataset_dir = self.exp_conf.dataset_conf.input_dir(self.secuml_conf)
        self.input_path = os.path.join(dataset_dir, 'features',
                                       self.features_conf.input_features)
        self._check()
        if not self.already_loaded:
            self._load_dataset_features()
        self._set_features_conf()

    def _set_features_conf(self):
        # Set dataset_features_id
        self.features_conf.dataset_features_id = self.dataset_features_id
        # Set features_files_ids
        query = self.session.query(FeaturesFilesAlchemy)
        query = query.filter(FeaturesFilesAlchemy.dataset_features_id ==
                             self.dataset_features_id)
        query = query.order_by(FeaturesFilesAlchemy.id)
        self.features_files_ids = [r.id for r in query.all()]
        self.features_conf.features_files_ids = self.features_files_ids
        # Set input_type
        self.features_conf.input_type = self.input_type
        # Set filters in / out
        dataset_dir = self.exp_conf.dataset_conf.input_dir(self.secuml_conf)
        features_dir = os.path.join(dataset_dir, 'features')
        filter_in_f = self.features_conf.filter_in_filename
        filter_out_f = self.features_conf.filter_out_filename
        if filter_in_f is not None:
            with open(os.path.join(features_dir, filter_in_f)) as f:
                self.features_conf.filter_in = [r.rstrip()
                                                for r in f.readlines()]
        elif filter_out_f is not None:
            with open(os.path.join(features_dir, filter_out_f)) as f:
                self.features_conf.filter_out = [r.rstrip()
                                                 for r in f.readlines()]

    def _check(self):
        self._check_path_exists()
        self._check_already_loaded()
        if self.already_loaded:
            self._check_hashes()

    def _check_path_exists(self):
        if not (os.path.isfile(self.input_path) or
                os.path.isdir(self.input_path)):
            raise FeaturesNotFound(self.input_path)
        self._check_already_loaded()

    def _check_already_loaded(self):
        self.already_loaded = False
        self._set_input_features_type()
        query = self.session.query(DatasetFeaturesAlchemy)
        query = query.filter(DatasetFeaturesAlchemy.dataset_id ==
                             self.exp_conf.dataset_conf.dataset_id)
        query = query.filter(DatasetFeaturesAlchemy.name ==
                             self.features_conf.input_features)
        query = query.filter(DatasetFeaturesAlchemy.type ==
                             self.input_type.name)
        try:
            self.dataset_features_id = query.one().id
            self.already_loaded = True
        except NoResultFound:
            self.dataset_features_id = None

    def _load_dataset_features(self):
        dataset_features = DatasetFeaturesAlchemy(
                dataset_id=self.exp_conf.dataset_conf.dataset_id,
                name=self.features_conf.input_features,
                type=self.input_type.name)
        self.session.add(dataset_features)
        self.session.flush()
        self.dataset_features_id = dataset_features.id
        self._load_features_files()

    def _check_hashes(self):
        query = self.session.query(FeaturesFilesAlchemy)
        query = query.filter(FeaturesFilesAlchemy.dataset_features_id ==
                             self.dataset_features_id)
        db_files = {r.filename: r.hash for r in query.all()}
        if self.input_type == InputFeaturesTypes.file:
            files = [self.features_conf.input_features]
            dataset_dir = self.exp_conf.dataset_conf.input_dir(self.secuml_conf)
            features_path = os.path.join(dataset_dir, 'features')
        elif self.input_type == InputFeaturesTypes.dir:
            files = os.listdir(self.input_path)
            if len(files) != len(db_files):
                raise UpdatedDirectory(self.input_path, db_files.keys(), files)
            features_path = self.input_path
        for filename in files:
            file_path = os.path.join(features_path, filename)
            file_hash = compute_hash(file_path)
            if file_hash != db_files[filename]:
                raise UpdatedFile(file_path, self.exp_conf.dataset_conf.dataset)

    def _set_input_features_type(self):
        if os.path.isfile(self.input_path):
            self.input_type = InputFeaturesTypes.file
        elif os.path.isdir(self.input_path):
            self.input_type = InputFeaturesTypes.dir

    def _load_features_files(self):
        if self.input_type == InputFeaturesTypes.file:
            files = [(self.input_path, self.features_conf.input_features)]
        elif self.input_type == InputFeaturesTypes.dir:
            files = [(os.path.join(self.input_path, f), f)
                     for f in os.listdir(self.input_path)]
        for file_path, filename in files:
            self._load_features_file(file_path, filename)

    def _load_features_file(self, file_path, filename):
        file_hash = compute_hash(file_path)
        features_file = FeaturesFilesAlchemy(
                dataset_features_id=self.dataset_features_id,
                filename=filename,
                hash=file_hash)
        self.session.add(features_file)
        self.session.flush()
        self._load_features(features_file.id, file_path)

    def _load_features(self, file_id, file_path):
        # Main features file
        with open(file_path, 'r') as f_file:
            features_reader = csv.reader(f_file)
            ids = next(features_reader)[1:]
        # Description file
        basename, _ = os.path.splitext(file_path)
        description_file = '%s_description.csv' % basename
        if os.path.isfile(description_file):
            with open(description_file, 'r') as f:
                df = pd.read_csv(f, header=0, index_col=0)
                names = df['name']
                descriptions = df['description']
        else:
            names = ids
            descriptions = ids
        # Add features to the DB
        for id, name, description in zip(ids, names, descriptions):
            feature = FeaturesAlchemy(user_id=id, file_id=file_id,
                                      dataset_features_id=self.dataset_features_id,
                                      name=name, description=description)
            self.session.add(feature)
        self.session.flush()
