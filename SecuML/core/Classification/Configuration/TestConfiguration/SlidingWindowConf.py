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

from . import TestConfFactory
from .TestConfiguration import TestConfiguration


class SlidingWindowConf(TestConfiguration):

    def __init__(self, num_buckets, num_train_buckets, num_test_buckets,
                 alerts_conf=None):
        TestConfiguration.__init__(self, alerts_conf=alerts_conf)
        self.method = 'sliding_window'
        self.num_buckets = num_buckets
        self.num_train_buckets = num_train_buckets
        self.num_test_buckets = num_test_buckets
        self.computeNumFolds()

    def computeNumFolds(self):
        r = self.num_buckets
        r -= (self.num_train_buckets + self.num_test_buckets)
        r += 1
        self.num_folds = r

    def generateSuffix(self):
        buckets = [self.num_buckets,
                   self.num_train_buckets,
                   self.num_test_buckets]
        buckets = '_'.join(map(str, buckets))
        suffix = '__Test_SlidingWindow_' + buckets
        suffix += TestConfiguration.generateSuffix(self)
        return suffix

    @staticmethod
    def fromJson(obj):
        alerts_conf = TestConfiguration.alertConfFromJson(obj)
        conf = SlidingWindowConf(obj['num_buckets'],
                                 obj['num_train_buckets'],
                                 obj['num_test_buckets'],
                                 alerts_conf=alerts_conf)
        return conf

    def toJson(self):
        conf = TestConfiguration.toJson(self)
        conf['__type__'] = 'SlidingWindowConf'
        conf['num_buckets'] = self.num_buckets
        conf['num_train_buckets'] = self.num_train_buckets
        conf['num_test_buckets'] = self.num_test_buckets
        return conf

    @staticmethod
    def generateParamsFromArgs(args):
        params = TestConfiguration.generateParamsFromArgs(args)
        params['num_buckets'] = args.num_buckets
        params['num_train_buckets'] = args.num_train_buckets
        params['num_test_buckets'] = args.num_test_buckets
        return params


TestConfFactory.getFactory().registerClass('SlidingWindowConf',
                                           SlidingWindowConf)
