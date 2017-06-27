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

import json

from SecuML.Plots.PlotDataset import PlotDataset
from SecuML.Clustering.Evaluation.PerformanceIndicators import PerformanceIndicators
from SecuML.Tools import colors_tools

from AnnotationQueries.UncertainAnnotationQueries import UncertainAnnotationQueries
from AnnotationQueries.RareCategoryDetectionAnnotationQueries import RareCategoryDetectionAnnotationQueries
from QueryStrategy import QueryStrategy

class Ilab(QueryStrategy):

    def __init__(self, iteration):
        QueryStrategy.__init__(self, iteration)
        conf = iteration.experiment.conf
        eps = conf.eps
        self.uncertain = UncertainAnnotationQueries(self.iteration, conf.num_uncertain, 0, 1)
        self.malicious = RareCategoryDetectionAnnotationQueries(self.iteration, 'malicious', 1-eps, 1)
        self.benign    = RareCategoryDetectionAnnotationQueries(self.iteration, 'benign', 0, eps)

    def generateAnnotationQueries(self):
        self.generate_queries_time = 0
        self.uncertain.run()
        self.generate_queries_time += self.uncertain.generate_queries_time
        self.exportAnnotationsTypes(malicious = False, benign = False)
        uncertain_queries = self.uncertain.getInstanceIds()
        self.malicious.run(already_queried = uncertain_queries)
        self.generate_queries_time += self.malicious.generate_queries_time
        self.exportAnnotationsTypes(malicious = True, benign = False)
        self.benign.run(already_queried = uncertain_queries)
        self.generate_queries_time += self.benign.generate_queries_time
        self.exportAnnotationsTypes()
        self.globalClusteringEvaluation()

    def annotateAuto(self):
        self.uncertain.annotateAuto()
        self.malicious.annotateAuto()
        self.benign.annotateAuto()

    def getManualAnnotations(self):
        self.uncertain.getManualAnnotations()
        self.malicious.getManualAnnotations()
        self.benign.getManualAnnotations()

    def getClusteringsEvaluations(self):
        clusterings = {}
        clusterings['all']       = self.global_clustering_perf
        clusterings['malicious'] = None
        clusterings['benign']    = None
        return clusterings

    def globalClusteringEvaluation(self):
        clusters       = []
        true_families = []
        if self.malicious.categories is not None:
            clusters       += list(self.malicious.categories.assigned_categories)
            true_families += self.malicious.categories.instances.getFamilies(true_labels = True)
        if self.benign.categories is not None:
            max_clusters = 0
            if len(clusters) > 0:
                max_clusters = max(clusters)
            clusters       += [x + max_clusters + 1 for x in list(self.benign.categories.assigned_categories)]
            true_families += self.benign.categories.instances.getFamilies(true_labels = True)
        if len(clusters) > 0:
            self.global_clustering_perf = PerformanceIndicators()
            self.global_clustering_perf.generateEvaluation(clusters, true_families)
        else:
            self.global_clustering_perf = None

    ###############################
    ## Execution time monitoring ##
    ###############################

    def executionTimeHeader(self):
        header  = ['malicious_queries', 'uncertain_queries', 'benign_queries']
        return header

    def executionTimeMonitoring(self):
        line  = [self.malicious.analysis_time + self.malicious.generate_queries_time]
        line += [self.iteration.train_test_validation.times['binary'] + self.uncertain.generate_queries_time]
        line += [self.benign.analysis_time + self.benign.generate_queries_time]
        return line

    def executionTimeDisplay(self):
        uncertain = PlotDataset(None, 'Uncertain Queries')
        malicious = PlotDataset(None, 'Malicious Queries')
        malicious.setLinestyle('dotted')
        malicious.setColor(colors_tools.getLabelColor('malicious'))
        benign = PlotDataset(None, 'Benign Queries')
        benign.setLinestyle('dashed')
        benign.setColor(colors_tools.getLabelColor('benign'))
        return [malicious, uncertain, benign]

    def exportAnnotationsTypes(self, malicious = True, benign = True):
        types = {'uncertain': 'individual', 'malicious': None, 'benign': None}
        if malicious:
            types['malicious'] = self.malicious.annotations_type
        if benign:
            types['benign'] = self.benign.annotations_type
        filename  = self.iteration.output_directory
        filename += 'annotations_types.json'
        with open(filename, 'w') as f:
            json.dump(types, f, indent = 2)
