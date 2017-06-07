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

from AnnotationQueries.RareCategoryDetectionAnnotationQueries import RareCategoryDetectionAnnotationQueries
from QueryStrategy import QueryStrategy

class RareCategoryDetection(QueryStrategy):

    def __init__(self, iteration):
        QueryStrategy.__init__(self, iteration)
        multiclass_model = self.iteration.train_test_validation.models['multiclass']
        self.all_instances = RareCategoryDetectionAnnotationQueries(self.iteration, 'all', 0, 1,
                                                                    multiclass_model = multiclass_model)

    def generateAnnotationQueries(self):
        self.all_instances.run()
        self.generate_queries_time = self.all_instances.generate_queries_time
        self.exportAnnotationsTypes()

    def annotateAuto(self):
        self.all_instances.annotateAuto()

    def getManualAnnotations(self):
        self.all_instances.getManualAnnotations()

    def getClusteringsEvaluations(self):
        clusterings = {}
        clusterings['all'] = None
        return clusterings

    ###############################
    ## Execution time monitoring ##
    ###############################

    def executionTimeHeader(self):
        header  = ['clustering']
        header += QueryStrategy.executionTimeHeader(self)
        return header

    def executionTimeMonitoring(self):
        line  = [self.all_instances.analysis_time]
        line += QueryStrategy.executionTimeMonitoring(self)
        return line

    def executionTimeDisplay(self):
        clustering = PlotDataset(None, 'Analysis')
        return [clustering] + QueryStrategy.executionTimeDisplay(self)

    def exportAnnotationsTypes(self):
        clustering_exp = self.all_instances.clustering_exp
        if clustering_exp is not None:
            clustering_exp = clustering_exp.experiment_id
        types = {'all': {'type': self.all_instances.annotations_type,
                         'clustering_exp': clustering_exp
                        }
                }
        filename  = self.iteration.output_directory
        filename += 'annotations_types.json'
        with open(filename, 'w') as f:
            json.dump(types, f, indent = 2)
