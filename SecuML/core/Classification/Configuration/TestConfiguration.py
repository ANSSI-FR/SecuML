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

from .AlertsConfiguration import AlertsConfiguration


class TestConfiguration(object):

    def __init__(self, alerts_conf=None):
        self.method = None
        self.alerts_conf = alerts_conf

    def setTestDataset(self, test_dataset):
        self.method = 'dataset'
        self.test_dataset = test_dataset

    def setRandomSplit(self, test_size):
        self.method = 'random_split'
        self.test_size = test_size

    def setCvNumFolds(self, num_folds):
        self.method = 'cv'
        self.num_folds = num_folds

    def setUnlabeled(self):
        self.method = 'unlabeled'

    def generateSuffix(self):
        if self.method == 'dataset':
            suffix = '__Test_' + self.test_dataset
        elif self.method == 'random_split':
            suffix = '__Test' + str(int(self.test_size * 100))
        elif self.method == 'cv':
            suffix = '__Test' + str(self.num_folds)
        elif self.method == 'unlabeled':
            suffix = '__UnlabeledLabeled'
        if self.alerts_conf is not None:
            suffix += self.alerts_conf.generateSuffix()
        return suffix

    @staticmethod
    def fromJson(obj):
        alerts_conf = None
        if obj['alerts_conf'] is not None:
            alerts_conf = AlertsConfiguration.fromJson(
                obj['alerts_conf'])
        conf = TestConfiguration(alerts_conf=alerts_conf)
        conf.method = obj['method']
        if obj['method'] == 'dataset':
            conf.setTestDataset(obj['test_dataset'])
        elif obj['method'] == 'random_split':
            conf.setRandomSplit(obj['test_size'])
        elif obj['method'] == 'cv':
            conf.setCvNumFolds(obj['num_folds'])
        elif obj['method'] == 'unlabeled':
            conf.setUnlabeled()
        elif obj['method'] == 'dataset':
            conf.method = 'dataset'
        return conf

    def toJson(self):
        conf = {}
        conf['__type__'] = 'TestConfiguration'
        conf['method'] = self.method
        if self.method == 'dataset':
            conf['test_dataset'] = self.test_dataset
        elif self.method == 'random_split':
            conf['test_size'] = self.test_size
        elif self.method == 'cv':
            conf['num_folds'] = self.num_folds
        conf['alerts_conf'] = None
        if self.alerts_conf is not None:
            conf['alerts_conf'] = self.alerts_conf.toJson()
        return conf
