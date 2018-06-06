# SecuML
# Copyright (C) 2017  ANSSI
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

import json

from SecuML.core.ActiveLearning.QueryStrategies.Ilab import Ilab
from SecuML.core.Data import labels_tools

from . import ActiveLearningStrategyFactoryExp
from .AnnotationQueries.RareCategoryDetectionAnnotationQueriesExp import RareCategoryDetectionAnnotationQueriesExp
from .AnnotationQueries.UncertainAnnotationQueriesExp import UncertainAnnotationQueriesExp


class IlabExp(Ilab):

    def setQueries(self):
        eps = self.iteration.conf.eps
        self.uncertain = UncertainAnnotationQueriesExp(self.iteration,
                                                       self.iteration.conf.num_uncertain, 0, 1)
        self.malicious = RareCategoryDetectionAnnotationQueriesExp(
            self.iteration, labels_tools.MALICIOUS, 1 - eps, 1,
            input_checking=False)
        self.benign = RareCategoryDetectionAnnotationQueriesExp(
            self.iteration, labels_tools.BENIGN, 0, eps,
            input_checking=False)

    def generateAnnotationQueries(self):
        self.generate_queries_time = 0
        self.uncertain.run()
        self.generate_queries_time += self.uncertain.generate_queries_time
        self.exportAnnotationsTypes(malicious=False, benign=False)
        uncertain_queries = self.uncertain.getInstanceIds()
        self.malicious.run(already_queried=uncertain_queries)
        self.generate_queries_time += self.malicious.generate_queries_time
        self.exportAnnotationsTypes(malicious=True, benign=False)
        self.benign.run(already_queried=uncertain_queries)
        self.generate_queries_time += self.benign.generate_queries_time
        self.exportAnnotationsTypes()
        self.globalClusteringEvaluation()

    def exportAnnotationsTypes(self, malicious=True, benign=True):
        types = {'uncertain': {'type': 'individual', 'clustering_exp': None},
                 labels_tools.MALICIOUS: None,
                 labels_tools.BENIGN: None}
        if malicious:
            types[labels_tools.MALICIOUS] = {}
            types[labels_tools.MALICIOUS]['type'] = self.malicious.annotations_type
            clustering_exp = self.malicious.clustering_exp
            if clustering_exp is not None:
                types[labels_tools.MALICIOUS]['clustering_exp'] = clustering_exp.experiment_id
            else:
                types[labels_tools.MALICIOUS]['clustering_exp'] = None
        if benign:
            types[labels_tools.BENIGN] = {}
            types[labels_tools.BENIGN]['type'] = self.benign.annotations_type
            clustering_exp = self.benign.clustering_exp
            if clustering_exp is not None:
                types[labels_tools.BENIGN]['clustering_exp'] = clustering_exp.experiment_id
            else:
                types[labels_tools.BENIGN]['clustering_exp'] = None
        filename = self.iteration.iteration_dir
        filename += 'annotations_types.json'
        with open(filename, 'w') as f:
            json.dump(types, f, indent=2)


ActiveLearningStrategyFactoryExp.getFactory().registerClass('IlabExp',
                                                            IlabExp)
