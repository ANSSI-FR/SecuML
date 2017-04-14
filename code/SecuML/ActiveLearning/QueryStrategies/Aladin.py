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

from SecuML.Plots.PlotDataset import PlotDataset

from AnnotationQueries.AladinAnnotationQueries import AladinAnnotationQueries
from QueryStrategy import QueryStrategy

class Aladin(QueryStrategy):

    def __init__(self, iteration):
        QueryStrategy.__init__(self, iteration)
        self.unsure = AladinAnnotationQueries(self.iteration, self.conf)

    def generateAnnotationQueries(self):
        self.unsure.run()
        self.generate_queries_time = self.unsure.generate_queries_time

    def annotateAuto(self):
        self.unsure.annotateAuto()

    def getClusteringsEvaluations(self):
        clusterings = {}
        clusterings['all'] = self.unsure.clustering_perf
        return clusterings

    ###############################
    ## Execution time monitoring ##
    ###############################

    def executionTimeHeader(self):
        header  = ['logistic_regression', 'naive_bayes']
        header += QueryStrategy.executionTimeHeader(self)
        return header

    def executionTimeMonitoring(self):
        line  = [self.unsure.lr_time, self.unsure.nb_time]
        line += QueryStrategy.executionTimeMonitoring(self)
        return line

    def executionTimeDisplay(self):
        lr = PlotDataset(None, 'Logistic Regression')
        lr.setLinestyle('dotted')
        nb = PlotDataset(None, 'Naive Bayes')
        nb.setLinestyle('dashed')
        return [lr, nb] + QueryStrategy.executionTimeDisplay(self)
