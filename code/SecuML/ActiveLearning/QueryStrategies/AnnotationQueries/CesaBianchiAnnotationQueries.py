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

from __future__ import division
import numpy as np
import random

from SecuML.ActiveLearning.CheckPredictedLabels import CheckPredictedLabels
from SecuML.Experiment import experiment_db_tools

from AnnotationQueries import AnnotationQueries

class CesaBianchiAnnotationQueries(AnnotationQueries):

    def __init__(self, iteration, b, num_annotations):
        AnnotationQueries.__init__(self, iteration)
        self.b = b
        self.num_annotations = num_annotations

    def addPredictedLabels(self):
        instances = self.predictions.index
        predicted_scores = self.predictions.loc[:, 'scores']
        proba  = [self.b / (self.b + abs(s)) for s in predicted_scores]
        # Not a fixed number of annotations at each iteration 
        #rand = [random.random() for s in predicted_scores]
        #for i in range(len(instances)):
        #    if rand[i] <= proba[i]:
        #        self.annotation_queries.append(instances[i])
        # Fixed number of annotations at each iteration
        sum_proba = sum(proba)
        norm_proba = [p/sum_proba for p in proba]
        self.annotation_queries = list(np.random.choice(instances, size = self.num_annotations, 
            replace = False, p = norm_proba))
    
    def analyzePredictedLabels(self):
        experiment_db_tools.addPredictedLabelsAnalysis(
                self.iteration.experiment.cursor,
                self.iteration.experiment.experiment_id,
                self.iteration.iteration_number,
                'CesaBianchi',
                False)
    
    def generateAnnotationQueries(self):
        self.exportAnnotationQueries(self.annotation_queries, 'CesaBianchi')
   
    def annotateAuto(self):
        self.add_labels = CheckPredictedLabels(self.iteration)
        true_labels = self.add_labels.getTrueLabels(self.annotation_queries)
        true_sublabels = self.add_labels.getTrueSublabels(self.annotation_queries)
        for i in range(len(self.annotation_queries)):
            self.add_labels.addLabel(self.annotation_queries[i], true_labels[i],
                    true_sublabels[i], 'CesaBianchi' + '__annotation',
                    True)
