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


class CutoffTimeConf(TestConfiguration):

    def __init__(self, cutoff_time, alerts_conf=None):
        TestConfiguration.__init__(self, alerts_conf=alerts_conf)
        self.method = 'cutoff_time'
        self.cutoff_time = cutoff_time

    def generateSuffix(self):
        suffix = '_Test_CuttOffTime_' + str(self.cutoff_time)
        suffix += TestConfiguration.generateSuffix(self)
        return suffix

    @staticmethod
    def fromJson(obj):
        alerts_conf = TestConfiguration.alertConfFromJson(obj)
        conf = CutoffTimeConf(obj['cutoff_time'], alerts_conf)
        return conf

    def toJson(self):
        conf = TestConfiguration.toJson(self)
        conf['__type__'] = 'CutoffTimeConf'
        conf['cutoff_time'] = str(self.cutoff_time)
        return conf

    @staticmethod
    def generateParamsFromArgs(args):
        params = TestConfiguration.generateParamsFromArgs(args)
        params['cutoff_time'] = args.cutoff_time
        return params


TestConfFactory.getFactory().registerClass('CutoffTimeConf',
                                           CutoffTimeConf)
