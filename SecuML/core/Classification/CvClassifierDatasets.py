# SecuML
# Copyright (C) 2017-2018  ANSSI
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

from __future__ import division
from sklearn.model_selection import StratifiedKFold

from .ClassifierDatasets import ClassifierDatasets


class CvClassifierDatasets(object):

    def __init__(self, test_conf, families_supervision, sample_weight, cv=None):
        self.test_conf = test_conf
        self.families_supervision = families_supervision
        self.sample_weight = sample_weight
        self.cv = cv
        self.datasets = []

    def getFeaturesNames(self):
        return self.datasets[0].train_instances.features.getNames()

    def generateDatasets(self, instances, test_instances=None):
        instances = instances.getAnnotatedInstances()
        self.generateFolds(instances)

    def generateFolds(self, instances):
        cv_split = self.generateSplit(instances)
        for fold_id, (train_ids, test_ids) in enumerate(cv_split):
            train_instances = instances.getInstancesFromIds(train_ids)
            test_instances = instances.getInstancesFromIds(test_ids)
            dataset = ClassifierDatasets(None, self.sample_weight)
            dataset.setDatasets(train_instances, test_instances)
            self.datasets.append(dataset)

    def generateSplit(self, instances):
        if self.test_conf.method == 'cv':
            cv_split = self.generateCvSplit(instances)
        elif self.test_conf.method == 'temporal_cv':
            cv_split = self.generateTemporalCvSplit(instances)
        elif self.test_conf.method == 'sliding_window':
            cv_split = self.generateSlidingWindowSplit(instances)
        else:
            assert(False)
        return cv_split

    def generateCvSplit(self, instances):
        cv = self.cv
        if cv is None:
            cv = StratifiedKFold(n_splits=self.test_conf.num_folds)
        annotations = instances.getAnnotations(False)
        supervision = annotations.getSupervision(self.families_supervision)
        cv_split = cv.split(instances.features.getValues(), supervision)
        # cv_split with instance_ids instead of indexes
        cv_split_ids = [None for _ in range(self.test_conf.num_folds)]
        for i, (train, test) in enumerate(cv_split):
            train_ids = [instances.ids.ids[t] for t in train]
            test_ids = [instances.ids.ids[t] for t in test]
            cv_split_ids[i] = (train_ids, test_ids)
        return cv_split_ids

    def generateTemporalCvSplit(self, instances):
        t_indexes, t_start, t_end = self.getSortedTimestamps(instances)
        num_buckets = self.test_conf.num_folds + 1
        delta = (t_end - t_start) / num_buckets
        cv_split = [None for _ in range(self.test_conf.num_folds)]
        cutoff_time = t_start + delta
        for i in range(self.test_conf.num_folds):
            train = instances.ids.getIdsBefore(cutoff_time)
            test = instances.ids.getIdsAfter(cutoff_time)
            cv_split[i] = (train, test)
            cutoff_time += delta
        return cv_split

    def generateSlidingWindowSplit(self, instances):
        t_indexes, t_start, t_end = self.getSortedTimestamps(instances)
        delta = (t_end - t_start) / self.test_conf.num_buckets
        cv_split = [None for _ in range(self.test_conf.num_folds)]
        start = t_start
        for i in range(self.test_conf.num_folds):
            train_start, train_end, test_start, test_end = \
                    self.computeSlidingWindows(start,
                                               self.test_conf.num_train_buckets,
                                               self.test_conf.num_test_buckets,
                                               delta)
            train = instances.ids.getIdsBetween(train_start, train_end)
            test = instances.ids.getIdsBetween(test_start, test_end)
            cv_split[i] = (train, test)
            start += delta
        return cv_split

    def computeSlidingWindows(self, t_start, num_train_buckets,
                              num_test_buckets, delta):
        train_start = t_start
        train_end = train_start + num_train_buckets * delta
        test_start = train_end
        test_end = test_start + num_test_buckets * delta
        return train_start, train_end, test_start, test_end

    def getSortedTimestamps(self, instances):
        timestamps = instances.ids.timestamps
        indexes = list(range(instances.numInstances()))
        t_indexes = list(zip(timestamps, indexes))
        t_indexes.sort()
        t_start = t_indexes[0][0]
        t_end = t_indexes[-1][0]
        return t_indexes, t_start, t_end
