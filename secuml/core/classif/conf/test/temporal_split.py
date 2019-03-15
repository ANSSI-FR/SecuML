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
from secuml.core.tools.float import to_percentage

from . import OneFoldTestConf


class TemporalSplitConf(OneFoldTestConf):

    def __init__(self, logger, alerts_conf, test_size):
        OneFoldTestConf.__init__(self, logger, alerts_conf)
        self.method = 'temporal_split'
        self.test_size = test_size

    def get_exp_name(self):
        return '__Test_TemporalSplit_%s_%s' % (
                                            to_percentage(self.test_size),
                                            OneFoldTestConf.get_exp_name(self))

    def fields_to_export(self):
        fields = OneFoldTestConf.fields_to_export(self)
        fields.extend([('test_size', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def gen_parser(parser):
        parser.add_argument('--test-size-temp',
                            type=float,
                            default=0.1,
                            help='Pourcentage of the training data selected '
                                 'for validation. '
                                 'Default: 0.1')

    @staticmethod
    def from_args(args, logger):
        alerts_conf = OneFoldTestConf.alert_conf_from_args(args, logger)
        return TemporalSplitConf(logger, alerts_conf, args.test_size_temp)

    @staticmethod
    def from_json(obj, logger):
        alerts_conf = OneFoldTestConf.alert_conf_from_json(obj, logger)
        return TemporalSplitConf(logger, alerts_conf, obj['test_size'])

    def _gen_train_test(self, classifier_conf, instances):
        timestamps = instances.ids.timestamps
        ids = instances.ids.ids
        t_ids = list(zip(timestamps, ids))
        t_ids.sort()
        num_train = int(len(t_ids) * (1 - self.test_size))
        train = [i for t, i in t_ids[:num_train]]
        test = [i for t, i in t_ids[num_train:]]
        train_instances = instances.get_from_ids(train)
        test_instances = instances.get_from_ids(test)
        return train_instances, test_instances
