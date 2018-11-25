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

from SecuML.core.Conf import exportFieldMethod
from SecuML.core.tools import date_tools

from . import TestConfFactory
from .OneFoldTestConf import OneFoldTestConf


class CutoffTimeConf(OneFoldTestConf):

    def __init__(self, logger, alerts_conf, cutoff_time):
        OneFoldTestConf.__init__(self, logger, alerts_conf)
        self.method = 'cutoff_time'
        self.cutoff_time = cutoff_time

    def get_exp_name(self):
        name = '_Test_CuttOffTime_' + str(self.cutoff_time)
        name += OneFoldTestConf.get_exp_name(self)
        return name

    def fieldsToExport(self):
        fields = OneFoldTestConf.fieldsToExport(self)
        fields.extend([('cutoff_time', exportFieldMethod.string)])
        return fields

    @staticmethod
    def generateParser(parser):
        parser.add_argument('--cutoff-time',
                 type=date_tools.valid_date,
                 help='Cutoff time. Format: YYYY-MM-DD HH:MM:SS. ')

    @staticmethod
    def fromArgs(args, logger):
        alerts_conf = OneFoldTestConf.alertConfFromArgs(args, logger)
        return CutoffTimeConf(logger, alerts_conf, args.cutoff_time)

    @staticmethod
    def from_json(obj, logger):
        alerts_conf = OneFoldTestConf.alertConfFromJson(obj, logger)
        return CutoffTimeConf(logger, alerts_conf, obj['cutoff_time'])


TestConfFactory.getFactory().registerClass('CutoffTimeConf', CutoffTimeConf)
