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
from SecuML.core.tools import floats_tools

from . import TestConfFactory
from .OneFoldTestConf import OneFoldTestConf


class TemporalSplitConf(OneFoldTestConf):

    def __init__(self, logger, alerts_conf, test_size):
        OneFoldTestConf.__init__(self, logger, alerts_conf)
        self.method = 'temporal_split'
        self.test_size = test_size

    def get_exp_name(self):
        name = '__Test_TemporalSplit_%s' \
                 % floats_tools.toPercentage(self.test_size)
        name += OneFoldTestConf.get_exp_name(self)
        return name

    def fieldsToExport(self):
        fields = OneFoldTestConf.fieldsToExport(self)
        fields.extend([('test_size', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def generateParser(parser):
        parser.add_argument('--test-size-temp',
                            type=float,
                            default=0.1,
                            help='Pourcentage of the training data selected '
                                 'for validation. '
                                 'Default: 0.1')

    @staticmethod
    def fromArgs(args, logger):
        alerts_conf = OneFoldTestConf.alertConfFromArgs(args, logger)
        return TemporalSplitConf(logger, alerts_conf, args.test_size_temp)

    @staticmethod
    def from_json(obj, logger):
        alerts_conf = OneFoldTestConf.alertConfFromJson(obj, logger)
        return TemporalSplitConf(logger, alerts_conf, obj['test_size'])


TestConfFactory.getFactory().registerClass('TemporalSplitConf',
                                           TemporalSplitConf)
