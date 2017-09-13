## SecuML
## Copyright (C) 2016  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

import random

from AnnotationQueries import AnnotationQueries
from AnnotationQuery   import AnnotationQuery

class RandomAnnotationQueries(AnnotationQueries):

    def __init__(self, iteration, num_annotations):
        AnnotationQueries.__init__(self, iteration, 'random')
        self.num_annotations = num_annotations

    def runModels(self):
        return

    def generateAnnotationQueries(self):
        if len(self.predictions.index) > self.num_annotations:
            df_queries = self.predictions.loc[random.sample(list(self.predictions.index), self.num_annotations)]
        else:
            df_queries = self.predictions
        for index, row in df_queries.iterrows():
            query = AnnotationQuery(index, row['predicted_proba'], None, None)
            self.annotation_queries.append(query)
