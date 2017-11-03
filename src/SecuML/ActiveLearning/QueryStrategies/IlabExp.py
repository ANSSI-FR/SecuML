## SecuML
## Copyright (C) 2017  ANSSI
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

from AnnotationQueries.RareCategoryDetectionAnnotationQueriesExp import RareCategoryDetectionAnnotationQueriesExp
from AnnotationQueries.UncertainAnnotationQueries import UncertainAnnotationQueries

from Ilab import Ilab
from QueryStrategy import QueryStrategy

class IlabExp(Ilab):

    def __init__(self, iteration):
        QueryStrategy.__init__(self, iteration)
        eps = self.iteration.conf.eps
        self.uncertain = UncertainAnnotationQueries(self.iteration, self.iteration.conf.num_uncertain, 0, 1)
        self.malicious = RareCategoryDetectionAnnotationQueriesExp(self.iteration, 'malicious', 1-eps, 1)
        self.benign    = RareCategoryDetectionAnnotationQueriesExp(self.iteration, 'benign', 0, eps)

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

    def exportAnnotationsTypes(self, malicious = True, benign = True):
        types = {'uncertain': {'type': 'individual', 'clustering_exp': None},
                 'malicious': None,
                 'benign': None}
        if malicious:
            types['malicious'] = {}
            types['malicious']['type'] = self.malicious.annotations_type
            clustering_exp = self.malicious.clustering_exp
            if clustering_exp is not None:
                types['malicious']['clustering_exp'] = clustering_exp.experiment_id
            else:
                types['malicious']['clustering_exp'] = None
        if benign:
            types['benign'] = {}
            types['benign']['type'] = self.benign.annotations_type
            clustering_exp = self.benign.clustering_exp
            if clustering_exp is not None:
                types['benign']['clustering_exp'] = clustering_exp.experiment_id
            else:
                types['benign']['clustering_exp'] = None
        filename  = self.iteration.iteration_dir
        filename += 'annotations_types.json'
        with open(filename, 'w') as f:
            json.dump(types, f, indent = 2)
