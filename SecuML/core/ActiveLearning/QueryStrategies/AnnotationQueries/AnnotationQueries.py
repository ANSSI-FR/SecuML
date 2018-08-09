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

import abc
import numpy as np
import os.path as path
import pandas as pd
import time

from .AnnotationQuery import AnnotationQuery


class AnnotationQueries(object):

    def __init__(self, iteration, label):
        self.iteration = iteration
        self.label = label
        self.annotation_queries = []

    def run(self):
        self.predictions = self.getPredictedProbabilities()
        self.runModels()
        start_time = time.time()
        self.generateAnnotationQueries()
        self.generate_queries_time = time.time() - start_time
        self.exportAnnotationQueries()

    @abc.abstractmethod
    def runModels(self):
        return

    @abc.abstractmethod
    def generateAnnotationQueries(self):
        return

    def generateAnnotationQuery(self, instance_id, predicted_proba,
                                suggested_label, suggested_family, confidence=None):
        return AnnotationQuery(instance_id, predicted_proba,
                               suggested_label, suggested_family, confidence=confidence)

    def getPredictedProbabilities(self):
        models_conf = self.iteration.conf.models_conf
        if 'binary' in models_conf:
            classifier = self.iteration.update_model.models['binary']
            predictions = classifier.testing_monitoring.predictions_monitoring.predictions
        else:
            test_instances = self.iteration.datasets.getTestInstances()
            num_instances = test_instances.numInstances()
            predictions = pd.DataFrame(
                np.zeros((num_instances, 4)),
                index=test_instances.ids.getIds(),
                columns=['predicted_proba', 'predicted_labels', 'ground_truth', 'scores'])
            predictions['predicted_proba'] = [0.5] * num_instances
            predictions['predicted_labels'] = [False] * num_instances
            predictions['ground_truth'] = test_instances.ground_truth.getLabels()
            predictions['scores'] = [0.5] * num_instances
        return predictions

    def exportAnnotationQueries(self):
        iteration_dir = self.iteration.iteration_dir
        if iteration_dir is None:
            return
        filename = path.join(iteration_dir,
                             'toannotate_' + self.label + '.csv')
        with open(filename, 'w') as f:
            for i, annotation_query in enumerate(self.annotation_queries):
                if i == 0:
                    annotation_query.displayHeader(f)
                annotation_query.export(f)

    def annotateAuto(self):
        for annotation_query in self.annotation_queries:
            annotation_query.annotateAuto(self.iteration, self.label)

    def getManualAnnotations(self):
        for annotation_query in self.annotation_queries:
            annotation_query.getManualAnnotation(self.iteration)

    def checkAnnotationQueriesAnswered(self):
        for annotation_query in self.annotation_queries:
            if not annotation_query.checkAnswered(self.iteration):
                return False
        return True

    def getInstanceIds(self):
        return [annotation_query.instance_id
                for annotation_query in self.annotation_queries]
