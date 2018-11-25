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

from SecuML.core.tools.plots.PlotDataset import PlotDataset

from .queries.AladinQueries import AladinQueries
from .Strategy import Strategy


class Aladin(Strategy):

    def __init__(self, iteration):
        Strategy.__init__(self, iteration)
        self.setQueries()

    def setQueries(self):
        self.unsure = AladinQueries(self.iteration, self.conf)

    def generateQueries(self):
        self.unsure.run()
        self.generate_queries_time = self.unsure.generate_queries_time

    def annotateAuto(self):
        self.unsure.annotateAuto()

    def getManualAnnotations(self):
        self.unsure.getManualAnnotations()

    def getClusteringsEvaluations(self):
        clusterings = {}
        clusterings['all'] = self.unsure.clustering_perf
        return clusterings

    #############################
    # Execution time monitoring #
    #############################

    def executionTimeHeader(self):
        header = ['logistic_regression', 'naive_bayes']
        header.extend(Strategy.executionTimeHeader(self))
        return header

    def executionTimeMonitoring(self):
        line = [self.unsure.lr_time, self.unsure.nb_time]
        line.extend(Strategy.executionTimeMonitoring(self))
        return line

    def executionTimeDisplay(self):
        lr = PlotDataset(None, 'Logistic Regression')
        lr.set_linestyle('dotted')
        nb = PlotDataset(None, 'Naive Bayes')
        nb.set_linestyle('dashed')
        v = [lr, nb]
        v.extend(Strategy.executionTimeDisplay(self))
        return v
