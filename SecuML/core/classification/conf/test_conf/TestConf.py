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

from SecuML.core.classification.conf.AlertsConf import AlertsConf
from SecuML.core.Conf import Conf
from SecuML.core.Conf import exportFieldMethod

from . import TestConfFactory


class TestConf(Conf):

    def __init__(self, logger, alerts_conf):
        Conf.__init__(self, logger)
        self.method = None
        self.alerts_conf = alerts_conf

    def get_exp_name(self):
        return ''

    @staticmethod
    def generateParser(parser):
        factory = TestConfFactory.getFactory()
        methods = factory.getMethods()
        validation_group = parser.add_argument_group('Validation parameters')
        validation_group.add_argument('--validation-mode',
                 choices=methods,
                 default='RandomSplit',
                 help='Default: RandomSplit. '
                      'TemporalSplit, CutoffTime, TemporalCv, and '
                      'SlidingWindow require timestamped instances.')
        for method in methods:
            method_group = parser.add_argument_group(method + ' arguments')
            factory.generateParser(method, method_group)
        AlertsConf.generateParser(parser)

    @staticmethod
    def alertConfFromJson(obj, logger):
        if obj['alerts_conf'] is None:
            return None
        return AlertsConf.from_json(obj['alerts_conf'], logger)

    @staticmethod
    def alertConfFromArgs(args, logger):
        return AlertsConf.fromArgs(args, logger)

    def fieldsToExport(self):
        return [('method', exportFieldMethod.primitive),
                ('alerts_conf', exportFieldMethod.obj)]
