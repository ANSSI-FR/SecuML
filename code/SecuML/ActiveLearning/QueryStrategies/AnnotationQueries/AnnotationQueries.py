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

import abc
import pandas as pd

class AnnotationQueries(object):

    def __init__(self, iteration):
        self.iteration = iteration
        self.predictions = self.getPredictedProbabilities()
        self.annotation_queries = []
    
    def run(self):
        self.addPredictedLabels()
        self.analyzePredictedLabels()
        self.generateAnnotationQueries()
    
    @abc.abstractmethod
    def addPredictedLabels(self):
        return

    @abc.abstractmethod
    def analyzePredictedLabels(self):
        return

    @abc.abstractmethod
    def generateAnnotationQueries(self):
        return
    
    @abc.abstractmethod
    def annotateAuto(self):
        return

    def getPredictedProbabilities(self):
        classifier = self.iteration.train_test_validation.classifier
        predictions = classifier.testing_monitoring.\
                predictions_monitoring.predictions
        return predictions
    
    def exportAnnotationQueries(self, annotation_queries, label):
        filename  = self.iteration.output_directory
        filename += 'toannotate_' + label + '.csv'
        with open(filename, 'w') as f:
            for instance_id in annotation_queries:
                print >>f, instance_id
