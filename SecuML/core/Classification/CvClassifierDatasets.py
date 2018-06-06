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

    def __init__(self, families_supervision, num_folds, sample_weight, cv=None):
        self.families_supervision = families_supervision
        self.num_folds = num_folds
        self.sample_weight = sample_weight
        self.cv = cv
        self.datasets = []

    def getFeaturesNames(self):
        return self.datasets[0].train_instances.features.getNames()

    def generateDatasets(self, instances, test_instances=None):
        instances = instances.getAnnotatedInstances()
        self.generateFolds(instances)

    def generateFolds(self, instances):
        cv = self.cv
        if cv is None:
            cv = StratifiedKFold(n_splits=self.num_folds)
        annotations = instances.getAnnotations(False)
        supervision = annotations.getSupervision(self.families_supervision)
        cv_split = cv.split(instances.features.getValues(),
                            supervision)
        for fold_id, (train, test) in enumerate(cv_split):
            train_ids = [instances.ids.getIds()[i] for i in train]
            test_ids = [instances.ids.getIds()[i] for i in test]
            train_instances = instances.getInstancesFromIds(train_ids)
            test_instances = instances.getInstancesFromIds(test_ids)
            dataset = ClassifierDatasets(None, self.sample_weight)
            dataset.setDatasets(train_instances, test_instances)
            self.datasets.append(dataset)
