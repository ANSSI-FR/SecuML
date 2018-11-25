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

from . import TestConfFactory
from .OneFoldTestConf import OneFoldTestConf


class TestDatasetConf(OneFoldTestConf):

    def __init__(self, logger, alerts_conf, test_dataset):
        OneFoldTestConf.__init__(self, logger, alerts_conf)
        self.method = 'dataset'
        self.test_dataset = test_dataset

    def get_exp_name(self):
        name = '__Test_Dataset_' + self.test_dataset
        name += OneFoldTestConf.get_exp_name(self)
        return name

    def fieldsToExport(self):
        fields = OneFoldTestConf.fieldsToExport(self)
        fields.extend([('test_dataset', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def generateParser(parser):
        parser.add_argument('--test-dataset', default=None,
                            help='Name of the test dataset.')

    @staticmethod
    def fromArgs(args, logger):
        alerts_conf = OneFoldTestConf.alertConfFromArgs(args, logger)
        return TestDatasetConf(logger, alerts_conf, args.test_dataset)

    @staticmethod
    def from_json(obj, logger):
        alerts_conf = OneFoldTestConf.alertConfFromJson(obj, logger)
        return TestDatasetConf(logger, alerts_conf, obj['test_dataset'])


TestConfFactory.getFactory().registerClass('TestDatasetConf', TestDatasetConf)
