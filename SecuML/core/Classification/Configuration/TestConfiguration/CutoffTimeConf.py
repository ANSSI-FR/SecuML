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


class CutoffTimeConf(OneFoldTestConfiguration):

    def __init__(self, cutoff_time, alerts_conf=None, logger=None):
        OneFoldTestConfiguration.__init__(self, alerts_conf=alerts_conf, logger=logger)
        self.method = 'cutoff_time'
        self.cutoff_time = cutoff_time

    def generateSuffix(self):
        suffix = '_Test_CuttOffTime_' + str(self.cutoff_time)
        suffix += OneFoldTestConfiguration.generateSuffix(self)
        return suffix

    @staticmethod
    def fromJson(obj, logger=None):
        alerts_conf = OneFoldTestConfiguration.alertConfFromJson(obj, logger=logger)
        conf = CutoffTimeConf(obj['cutoff_time'], alerts_conf, logger=logger)
        return conf

    def toJson(self):
        conf = OneFoldTestConfiguration.toJson(self)
        conf['__type__'] = 'CutoffTimeConf'
        conf['cutoff_time'] = str(self.cutoff_time)
        return conf

    @staticmethod
    def generateParamsFromArgs(args, logger=None):
        params = OneFoldTestConfiguration.generateParamsFromArgs(args, logger=logger)
        params['cutoff_time'] = args.cutoff_time
        return params


TestConfFactory.getFactory().registerClass('CutoffTimeConf',
                                           CutoffTimeConf)
