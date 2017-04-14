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

from SecuML.Plots.PlotDataset import PlotDataset

class QueryStrategy(object):

    def __init__(self, iteration):
        self.iteration = iteration
        self.conf      = self.iteration.experiment.conf

    @abc.abstractmethod
    def generateAnnotationQueries(self):
        return

    @abc.abstractmethod
    def annotateAuto(self):
        return

    def getClusteringsEvaluations(self):
        return None

    ###############################
    ## Execution time monitoring ##
    ###############################

    def executionTimeHeader(self):
        return ['generate_queries']

    def executionTimeMonitoring(self):
        return [self.generate_queries_time]

    def executionTimeDisplay(self):
        generate_queries = PlotDataset(None, 'Queries generation')
        generate_queries.setColor('purple')
        return [generate_queries]
