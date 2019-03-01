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

from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold

from . import SeveralFoldsTestConf


class CvConf(SeveralFoldsTestConf):

    def __init__(self, logger, alerts_conf, num_folds):
        SeveralFoldsTestConf.__init__(self, logger, alerts_conf, num_folds)
        self.method = 'cv'

    def get_exp_name(self):
        name = '__Test_Cv_%d' % (self.num_folds)
        name += SeveralFoldsTestConf.get_exp_name(self)
        return name

    @staticmethod
    def gen_parser(parser):
        parser.add_argument('--num-folds-val',
                            type=int,
                            default=4,
                            help='Number of cross validation folds. '
                                 'Default: 4.')

    @staticmethod
    def from_args(args, logger):
        alerts_conf = SeveralFoldsTestConf.alert_conf_from_args(args, logger)
        return CvConf(logger, alerts_conf, args.num_folds_val)

    @staticmethod
    def from_json(obj, logger):
        alerts_conf = SeveralFoldsTestConf.alert_conf_from_json(obj, logger)
        return CvConf(logger, alerts_conf, obj['num_folds'])

    def _gen_cv_split(self, classifier_conf, instances):
        annotations = instances.get_annotations(False)
        supervision = annotations.get_supervision(classifier_conf.multiclass)
        # sklearn does not support StratifiedKFold if some instances are not
        # annotated (e.g. LabelPropagation).
        if any(l is None for l in supervision):
            cv = KFold(n_splits=self.num_folds)
        else:
            cv = StratifiedKFold(n_splits=self.num_folds)
        split = cv.split(instances.features.get_values(), supervision)
        # cv_split with instance_ids instead of indexes
        cv_split = [None for _ in range(self.num_folds)]
        for i, (train_indexes, test_indexes) in enumerate(split):
            train_ids = [instances.ids.ids[t] for t in train_indexes]
            test_ids = [instances.ids.ids[t] for t in test_indexes]
            cv_split[i] = (train_ids, test_ids)
        return cv_split
