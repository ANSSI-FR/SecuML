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


class CvConf(object):

    def __init__(self, num_folds, alerts_conf=None):
        TestConfiguration.__init__(self, alerts_conf=alerts_conf)
        self.method = 'cv'
        self.num_folds = num_folds

    def generateSuffix(self):
        suffix = '__Test_Cv_' + str(self.num_folds)
        suffix += TestConfiguration.generateSuffix(self)
        return suffix

    @staticmethod
    def fromJson(obj):
        alerts_conf = TestConfiguration.alertConfFromJson(obj)
        conf = CvConf(obj['num_folds'], alerts_conf)
        return conf

    def toJson(self):
        conf = TestConfiguration.toJson(self)
        conf['__type__'] = 'CvConf'
        conf['num_folds'] = self.num_folds
        return conf

    @staticmethod
    def generateParamsFromArgs(args):
        params = TestConfiguration.generateParamsFromArgs(args)
        params['num_folds'] = args.num_folds
        return params


TestConfFactory.getFactory().registerClass('CvConf',
                                           CvConf)
