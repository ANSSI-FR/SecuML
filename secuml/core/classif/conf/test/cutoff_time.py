# SecuML
# Copyright (C) 2016-2019  ANSSI
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

from secuml.core.conf import exportFieldMethod
from secuml.core.tools.date import valid_date

from . import OneFoldTestConf


class CutoffTimeConf(OneFoldTestConf):

    def __init__(self, logger, alerts_conf, cutoff_time):
        OneFoldTestConf.__init__(self, logger, alerts_conf)
        self.method = 'cutoff_time'
        self.cutoff_time = cutoff_time

    def get_exp_name(self):
        return '_Test_CuttOffTime_%s%s' % (str(self.cutoff_time),
                                           OneFoldTestConf.get_exp_name(self))

    def fields_to_export(self):
        fields = OneFoldTestConf.fields_to_export(self)
        fields.extend([('cutoff_time', exportFieldMethod.string)])
        return fields

    @staticmethod
    def gen_parser(parser):
        parser.add_argument('--cutoff-time',
                            type=valid_date,
                            help='Cutoff time. Format: YYYY-MM-DD HH:MM:SS. ')

    @staticmethod
    def from_args(args, logger):
        alerts_conf = OneFoldTestConf.alert_conf_from_args(args, logger)
        return CutoffTimeConf(logger, alerts_conf, args.cutoff_time)

    @staticmethod
    def from_json(obj, logger):
        alerts_conf = OneFoldTestConf.alert_conf_from_json(obj, logger)
        return CutoffTimeConf(logger, alerts_conf, obj['cutoff_time'])

    def _gen_train_test(self, classifier_conf, instances):
        train = instances.ids.get_ids_before(self.cutoff_time)
        test = instances.ids.get_ids_after(self.cutoff_time)
        train_instances = instances.get_from_ids(train)
        test_instances = instances.get_from_ids(test)
        return train_instances, test_instances
