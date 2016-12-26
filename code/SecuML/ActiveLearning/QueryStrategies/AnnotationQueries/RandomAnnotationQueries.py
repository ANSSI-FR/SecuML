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

from SecuML.ActiveLearning.CheckPredictedLabels import CheckPredictedLabels
from SecuML.Experiment import experiment_db_tools
from AnnotationQueries import AnnotationQueries

class RandomAnnotationQueries(AnnotationQueries):

    def __init__(self, iteration, num_annotations):
        AnnotationQueries.__init__(self, iteration)
        self.num_annotations = num_annotations

    def addPredictedLabels(self):
        unlabeled_ids = self.iteration.datasets.getUnlabeledInstances().getIds()
        if len(unlabeled_ids) > self.num_annotations:
            self.annotation_queries = random.sample(unlabeled_ids, self.num_annotations)
        else:
            self.annotation_queries = unlabeled_ids
    
    def analyzePredictedLabels(self):
        experiment_db_tools.addPredictedLabelsAnalysis(
                self.iteration.experiment.cursor,
                self.iteration.experiment.experiment_id,
                self.iteration.iteration_number,
                'random',
                False)
    
    def generateAnnotationQueries(self):
        self.exportAnnotationQueries(self.annotation_queries, 'random')
    
    def annotateAuto(self):
        self.add_labels = CheckPredictedLabels(self.iteration)
        true_labels = self.add_labels.getTrueLabels(self.annotation_queries)
        true_sublabels = self.add_labels.getTrueSublabels(self.annotation_queries)
        for i in range(len(self.annotation_queries)):
            self.add_labels.addLabel(self.annotation_queries[i], true_labels[i],
                    true_sublabels[i], 'random' + '__annotation',
                    True)
