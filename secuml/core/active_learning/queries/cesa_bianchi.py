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

import numpy as np
import pandas as pd

from . import Queries


class CesaBianchiQueries(Queries):

    def __init__(self, iteration, b, num_annotations):
        Queries.__init__(self, iteration)
        self.b = b
        self.num_annotations = num_annotations

    def run_models(self):
        return

    def generate_queries(self, already_queried=None):
        instances = self.predictions.ids.ids
        predicted_scores = self.predictions.scores
        proba = [self.b / (self.b + abs(s)) for s in predicted_scores]
        predictions_df = pd.DataFrame({'proba': proba}, index=instances)
        # drop already queried instances
        if already_queried is not None:
            predictions_df.drop(labels=already_queried, inplace=True)
        if len(predictions_df.index) < self.num_annotations:
            selected_df = predictions_df
        else:
            norm_proba = [p / sum(proba) for p in proba]
            selection = list(np.random.choice(instances,
                                              size=self.num_annotations,
                                              replace=False, p=norm_proba))
            selected_df = predictions_df.loc[selection]
        for index, row in selected_df.iterrows():
            query = self.generate_query(index, row['proba'], None, None)
            self.add_query(query)
