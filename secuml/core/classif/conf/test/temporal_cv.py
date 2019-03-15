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

from . import SeveralFoldsTestConf


class TemporalCvConf(SeveralFoldsTestConf):

    def __init__(self, logger, alerts_conf, num_folds):
        SeveralFoldsTestConf.__init__(self, logger, alerts_conf, num_folds)
        self.method = 'temporal_cv'

    def get_exp_name(self):
        name = '__Test_TemporalCv_%d' % (self.num_folds)
        name += SeveralFoldsTestConf.get_exp_name(self)
        return name

    @staticmethod
    def from_json(obj, logger):
        alerts_conf = SeveralFoldsTestConf.alert_conf_from_json(obj, logger)
        return TemporalCvConf(logger, alerts_conf, obj['num_folds'])

    @staticmethod
    def gen_parser(parser):
        parser.add_argument('--num-folds-val-temp',
                            type=int,
                            default=4,
                            help='Number of cross validation folds. '
                                 'Default: 4.')

    @staticmethod
    def from_args(args, logger):
        alerts_conf = SeveralFoldsTestConf.alert_conf_from_args(args, logger)
        return TemporalCvConf(logger, alerts_conf, args.num_folds_val_temp)

    def _gen_cv_split(self, classifier_conf, instances):
        t_indexes, t_start, t_end = instances.get_sorted_timestamps()
        num_buckets = self.num_folds + 1
        delta = (t_end - t_start) / num_buckets
        cv_split = [None for _ in range(self.num_folds)]
        cutoff_time = t_start + delta
        for i in range(self.num_folds):
            train = instances.ids.get_ids_before(cutoff_time)
            test = instances.ids.get_ids_between(cutoff_time,
                                                 cutoff_time + delta)
            cv_split[i] = (train, test)
            cutoff_time += delta
        return cv_split
