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

import pandas as pd

from secuml.core.tools.matrix import sort_data_frame

from . import Queries


class UncertainQueries(Queries):

    def __init__(self, iteration, num_annotations, label=None):
        Queries.__init__(self, iteration, label=label)
        self.num_annotations = num_annotations

    def run_models(self):
        return

    def generate_queries(self, already_queried=None):
        unsure_df = pd.DataFrame({'proba': self.predictions.probas},
                                 index=self.predictions.ids.ids)
        # drop already queried instances
        if already_queried is not None:
            unsure_df.drop(labels=already_queried, inplace=True)
        unsure_df['proba'] = abs(unsure_df['proba'] - 0.5)
        sort_data_frame(unsure_df, 'proba', True, True)
        if (self.num_annotations is not None and
                len(unsure_df) > self.num_annotations):
            unsure_df = unsure_df.head(n=self.num_annotations)
        for instance_id, row in unsure_df.iterrows():
            query = self.generate_query(instance_id, row['proba'], None, None)
            self.add_query(query)
