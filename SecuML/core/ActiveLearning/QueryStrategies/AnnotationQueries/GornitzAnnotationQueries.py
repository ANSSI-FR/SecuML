# SecuML
# Copyright (C) 2017-2018  ANSSI
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
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from SecuML.core.Tools import matrix_tools

from .AnnotationQueries import AnnotationQueries


class GornitzAnnotationQueries(AnnotationQueries):

    def __init__(self, iteration, num_annotations):
        AnnotationQueries.__init__(self, iteration, 'unsure')
        self.num_annotations = num_annotations
        self.num_neighbours = 10
        self.delta = 0.5

    def runModels(self):
        return

    def generateAnnotationQueries(self):
        predicted_scores = self.predictions['scores']
        if len(predicted_scores) == 0:
            return
        boundary_scores = abs(predicted_scores) / max(abs(predicted_scores))
        neighbours_scores = self.computeNeighboursScores()
        global_scores = self.delta * boundary_scores + \
            (1 - self.delta) * neighbours_scores
        queries_df = pd.DataFrame(data={'scores': predicted_scores,
                                        'boundary_scores': boundary_scores,
                                        'neighbours_scores': neighbours_scores,
                                        'global_scores': global_scores},
                                  index=self.predictions.index)
        matrix_tools.sortDataFrame(queries_df, 'global_scores', True, True)
        queries_df = queries_df.head(n=self.num_annotations)
        for index, row in queries_df.iterrows():
            query = self.generateAnnotationQuery(
                index, row['scores'], None, None)
            self.annotation_queries.append(query)

    def computeNeighboursScores(self):
        all_instances = self.iteration.datasets.instances
        # Connectivity matrix
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', NearestNeighbors(self.num_neighbours, n_jobs=-1))])
        pipeline.fit(all_instances.features.getValues())
        # Labels
        labels = np.array([generateLabel(x)
                           for x in all_instances.annotations.getLabels()])
        # Compute neighbour scores
        scores = []
        all_neighbours = pipeline.named_steps['model'].kneighbors(
            return_distance=False)
        for i, label in enumerate(labels):
            if label != 0:
                continue
            else:
                neighbours = all_neighbours[i]
                score = sum(labels[neighbours] + 1) / \
                    (2.0 * self.num_neighbours)
                scores.append(score)
        return np.array(scores)


def generateLabel(x):
    if x is None:
        return 0
    if x:
        return -1
    else:
        return 1
