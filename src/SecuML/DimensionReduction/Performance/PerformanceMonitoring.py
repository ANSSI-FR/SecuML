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

from ClassSeparation import ClassSeparation

class PerformanceMonitoring(object):

    def __init__(self, projection, experiment):
        self.class_separation      = ClassSeparation(projection)
        self.experiment            = experiment
        self.clustering_evaluation = None

    def computePerformance(self, instances):
        self.class_separation.computePerformance(instances)

    def finalComputations(self):
        return

    def display(self):
        return
