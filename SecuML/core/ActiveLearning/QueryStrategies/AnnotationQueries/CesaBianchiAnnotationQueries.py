# SecuML
# Copyright (C) 2016-2017  ANSSI
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

from .AnnotationQueries import AnnotationQueries


class CesaBianchiAnnotationQueries(AnnotationQueries):

    def __init__(self, iteration, b, num_annotations):
        AnnotationQueries.__init__(self, iteration, 'CesaBianchi')
        self.b = b
        self.num_annotations = num_annotations

    def runModels(self):
        return

    def generateAnnotationQueries(self):
        instances = self.predictions.index
        predicted_scores = self.predictions.loc[:, 'scores']
        proba = [self.b / (self.b + abs(s)) for s in predicted_scores]
        sum_proba = sum(proba)
        norm_proba = [p / sum_proba for p in proba]
        if len(instances) < self.num_annotations:
            selected_instance_ids = instances
        else:
            selected_instance_ids = list(np.random.choice(instances, size=self.num_annotations,
                                                          replace=False, p=norm_proba))
        selected_df = self.predictions.loc[selected_instance_ids]
        for index, row in selected_df.iterrows():
            query = self.generateAnnotationQuery(
                index, row['predicted_proba'], None, None)
            self.annotation_queries.append(query)
