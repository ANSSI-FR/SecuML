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


class Datasets(object):

    def __init__(self, train_instances, test_instances):
        self.train_instances = train_instances
        self.test_instances = test_instances

    def get_features_ids(self):
        return self.train_instances.features.get_ids()


class CvDatasets(object):

    def __init__(self):
        self._datasets = []

    def get_features_ids(self):
        return self._datasets[0].get_features_ids()

    def add_dataset(self, dataset):
        self._datasets.append(dataset)
