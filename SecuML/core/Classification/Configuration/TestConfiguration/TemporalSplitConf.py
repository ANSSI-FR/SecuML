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
from .OneFoldTestConfiguration import OneFoldTestConfiguration


class TemporalSplitConf(OneFoldTestConfiguration):

    def __init__(self, test_size, alerts_conf=None, logger=None):
        OneFoldTestConfiguration.__init__(self, alerts_conf=alerts_conf, logger=logger)
        self.method = 'temporal_split'
        self.test_size = test_size

    def generateSuffix(self):
        suffix = '__Test_TemporalSplit_%.0f%%' % (self.test_size*100)
        suffix += OneFoldTestConfiguration.generateSuffix(self)
        return suffix

    @staticmethod
    def fromJson(obj, logger=None):
        alerts_conf = OneFoldTestConfiguration.alertConfFromJson(obj, logger=logger)
        conf = TemporalSplitConf(obj['test_size'],
                                 alerts_conf=alerts_conf,
                                 logger=logger)
        return conf

    def toJson(self):
        conf = OneFoldTestConfiguration.toJson(self)
        conf['__type__'] = 'TemporalSplitConf'
        conf['test_size'] = self.test_size
        return conf

    @staticmethod
    def generateParamsFromArgs(args, logger=None):
        params = OneFoldTestConfiguration.generateParamsFromArgs(args, logger=logger)
        params['test_size'] = args.test_size
        return params


TestConfFactory.getFactory().registerClass('TemporalSplitConf',
                                           TemporalSplitConf)
