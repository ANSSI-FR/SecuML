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

from secuml.core.conf import exportFieldMethod

from . import SeveralFoldsTestConf


def _compute_num_folds(num_buckets, num_train_buckets, num_test_buckets):
    r = num_buckets
    r -= (num_train_buckets + num_test_buckets)
    r += 1
    return r


def _gen_sliding_windows(t_start, num_train_buckets, num_test_buckets, delta):
    train_start = t_start
    train_end = train_start + num_train_buckets * delta
    test_start = train_end
    test_end = test_start + num_test_buckets * delta
    return train_start, train_end, test_start, test_end


class SlidingWindowConf(SeveralFoldsTestConf):

    def __init__(self, logger, alerts_conf, num_buckets, num_train_buckets,
                 num_test_buckets):
        num_folds = _compute_num_folds(num_buckets, num_train_buckets,
                                       num_test_buckets)
        SeveralFoldsTestConf.__init__(self, logger, alerts_conf, num_folds)
        self.method = 'sliding_window'
        self.num_buckets = num_buckets
        self.num_train_buckets = num_train_buckets
        self.num_test_buckets = num_test_buckets

    def get_exp_name(self):
        buckets = [self.num_buckets,
                   self.num_train_buckets,
                   self.num_test_buckets]
        buckets = '_'.join(map(str, buckets))
        name = '__Test_SlidingWindow_' + buckets
        name += SeveralFoldsTestConf.get_exp_name(self)
        return name

    def fields_to_export(self):
        fields = SeveralFoldsTestConf.fields_to_export(self)
        fields.extend([('num_buckets', exportFieldMethod.primitive),
                       ('num_train_buckets', exportFieldMethod.primitive),
                       ('num_test_buckets', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def gen_parser(parser):
        parser.add_argument('--num-buckets',
                            type=int,
                            default=10,
                            help='Number of buckets. '
                                 'Default: 10.')
        parser.add_argument('--num-train-buckets',
                            type=int,
                            default=4,
                            help='Number of train buckets. '
                                 'Default: 4.')
        parser.add_argument('--num-test-buckets',
                            type=int,
                            default=1,
                            help='Number of test buckets. '
                                 'Default: 1.')

    @staticmethod
    def from_args(args, logger):
        alerts_conf = SeveralFoldsTestConf.alert_conf_from_args(args, logger)
        return SlidingWindowConf(logger, alerts_conf, args.num_buckets,
                                 args.num_train_buckets, args.num_test_buckets)

    @staticmethod
    def from_json(obj, logger):
        alerts_conf = SeveralFoldsTestConf.alert_conf_from_json(obj, logger)
        return SlidingWindowConf(logger,
                                 alerts_conf,
                                 obj['num_buckets'],
                                 obj['num_train_buckets'],
                                 obj['num_test_buckets'])

    def _gen_cv_split(self, classifier_conf, instances):
        t_indexes, t_start, t_end = instances.get_sorted_timestamps()
        delta = (t_end - t_start) / self.num_buckets
        cv_split = [None for _ in range(self.num_folds)]
        start = t_start
        for i in range(self.num_folds):
            train_start, train_end, test_start, test_end = \
                    _gen_sliding_windows(start,
                                         self.num_train_buckets,
                                         self.num_test_buckets,
                                         delta)
            train = instances.ids.get_ids_between(train_start, train_end)
            test = instances.ids.get_ids_between(test_start, test_end)
            cv_split[i] = (train, test)
            start += delta
        return cv_split
