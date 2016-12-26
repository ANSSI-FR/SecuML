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

import pandas as pd

from SecuML.ActiveLearning.CheckPredictedLabels import CheckPredictedLabels
from SecuML.Experiment import experiment_db_tools
from SecuML.Tools import matrix_tools

from AnnotationQueries import AnnotationQueries

class UncertainAnnotationQueries(AnnotationQueries):

    def __init__(self, iteration, num_annotations, proba_min, proba_max):
        AnnotationQueries.__init__(self, iteration)
        self.proba_min = proba_min
        self.proba_max = proba_max
        self.num_annotations = num_annotations

    def addPredictedLabels(self):
        unsure_df = matrix_tools.extractRowsWithThresholds(self.predictions,
                self.proba_min, self.proba_max, 'predicted_proba', deepcopy = True)
        unsure_df.loc[:, 'predicted_proba'] = abs(unsure_df.loc[:, 'predicted_proba'] - 0.5)
        unsure_df.sort(['predicted_proba'], inplace = True)
        if self.num_annotations is not None and len(unsure_df) > self.num_annotations:
            unsure_df = unsure_df.head(n = self.num_annotations)
        self.annotation_queries = unsure_df.index
    
    def analyzePredictedLabels(self):
        experiment_db_tools.addPredictedLabelsAnalysis(
                self.iteration.experiment.cursor,
                self.iteration.experiment.experiment_id,
                self.iteration.iteration_number,
                'unsure',
                False)
    
    def generateAnnotationQueries(self):
        self.exportAnnotationQueries(self.annotation_queries, 'unsure')
   
    def annotateAuto(self):
        self.add_labels = CheckPredictedLabels(self.iteration)
        true_labels = self.add_labels.getTrueLabels(self.annotation_queries)
        true_sublabels = self.add_labels.getTrueSublabels(self.annotation_queries)
        for i in range(len(self.annotation_queries)):
            self.add_labels.addLabel(self.annotation_queries[i], true_labels[i],
                    true_sublabels[i], 'unsure' + '__annotation',
                    True)
