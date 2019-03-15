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

import pandas as pd
from sklearn.metrics import make_scorer

from secuml.core.tools.matrix import sort_data_frame

from . import ObjectiveFuncConf


def ndcg(ground_truth, scores, pos_label=1):
    df = pd.DataFrame({'scores': scores,
                       'ground_truth': ground_truth,
                       'index': [0] * len(scores)})
    sort_data_frame(df, 'scores', False, True)
    df.loc[:, 'index'] = range(len(scores))
    selection = df.loc[:, 'ground_truth'] == pos_label
    df = df.loc[selection, :]
    score = sum([pow(2, -row['index']) for _, row in df.iterrows()])
    ideal_score = (sum([pow(2, -i) for i in range(len(scores))]))
    return score / ideal_score


class NdcgConf(ObjectiveFuncConf):

    def get_scoring_method(self):
        return make_scorer(ndcg, greater_is_better=True, needs_threshold=True)

    @staticmethod
    def gen_parser(parser):
        return

    @staticmethod
    def from_json(obj, logger):
        return NdcgConf(logger)

    @staticmethod
    def from_args(args, logger):
        return NdcgConf(logger)
