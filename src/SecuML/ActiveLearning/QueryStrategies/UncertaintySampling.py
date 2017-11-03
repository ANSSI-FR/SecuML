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

from AnnotationQueries.UncertainAnnotationQueries import UncertainAnnotationQueries
from QueryStrategy import QueryStrategy

class UncertaintySampling(QueryStrategy):

    def __init__(self, iteration):
        QueryStrategy.__init__(self, iteration)
        num_annotations = self.iteration.conf.batch
        proba_min = None
        proba_max = None
        self.annotations = UncertainAnnotationQueries(self.iteration, num_annotations, proba_min, proba_max)

    def generateAnnotationQueries(self):
        self.annotations.run()
        self.generate_queries_time = self.annotations.generate_queries_time

    def annotateAuto(self):
        self.annotations.annotateAuto()

    def getManualAnnotations(self):
        self.annotations.getManualAnnotations()

    ###############################
    ## Execution time monitoring ##
    ###############################

    def executionTimeHeader(self):
        header  = ['binary_model']
        header += QueryStrategy.executionTimeHeader(self)
        return header

    def executionTimeMonitoring(self):
        line  = [self.iteration.update_model.times['binary']]
        line += QueryStrategy.executionTimeMonitoring(self)
        return line

    def executionTimeDisplay(self):
        binary_model = PlotDataset(None, 'Binary model')
        return [binary_model] + QueryStrategy.executionTimeDisplay(self)
