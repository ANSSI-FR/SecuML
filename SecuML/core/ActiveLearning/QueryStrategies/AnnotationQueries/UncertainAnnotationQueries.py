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

from SecuML.core.Tools import matrix_tools

from .AnnotationQueries import AnnotationQueries


class UncertainAnnotationQueries(AnnotationQueries):

    def __init__(self, iteration, num_annotations, proba_min, proba_max):
        AnnotationQueries.__init__(self, iteration, 'uncertain')
        self.proba_min = proba_min
        self.proba_max = proba_max
        self.num_annotations = num_annotations

    def runModels(self):
        return

    def generateAnnotationQueries(self):
        unsure_df = matrix_tools.extractRowsWithThresholds(self.predictions,
                                                           self.proba_min, self.proba_max, 'predicted_proba', deepcopy=True)
        unsure_df['predicted_proba'] = abs(unsure_df['predicted_proba'] - 0.5)
        matrix_tools.sortDataFrame(unsure_df, 'predicted_proba', True, True)
        if self.num_annotations is not None and len(unsure_df) > self.num_annotations:
            unsure_df = unsure_df.head(n=self.num_annotations)
        for instance_id, row in unsure_df.iterrows():
            query = self.generateAnnotationQuery(
                instance_id, row['predicted_proba'], None, None)
            self.annotation_queries.append(query)
