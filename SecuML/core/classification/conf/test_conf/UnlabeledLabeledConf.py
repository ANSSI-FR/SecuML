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
from .OneFoldTestConf import OneFoldTestConf


class UnlabeledLabeledConf(OneFoldTestConf):

    def __init__(self, logger, alerts_conf):
        OneFoldTestConf.__init__(self, logger, alerts_conf)
        self.method = 'unlabeled'

    def get_exp_name(self):
        name = '__UnlabeledLabeled'
        name += OneFoldTestConf.get_exp_name(self)
        return name

    @staticmethod
    def generateParser(parser):
        return

    @staticmethod
    def fromArgs(args, logger):
        alerts_conf = OneFoldTestConf.alertConfFromArgs(args, logger)
        return UnlabeledLabeledConf(logger, alerts_conf)

    @staticmethod
    def from_json(obj, logger):
        alerts_conf = OneFoldTestConf.alertConfFromJson(obj, logger)
        return UnlabeledLabeledConf(logger, alerts_conf)


TestConfFactory.getFactory().registerClass('UnlabeledLabeledConf',
                                           UnlabeledLabeledConf)
