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

from AnnotationQueries.UncertainAnnotationQueries import UncertainAnnotationQueries
from AnnotationQueries.ConfidentAnnotationQueries import ConfidentAnnotationQueries

class ILAB(object):

    def __init__(self, iteration):
        ilab_conf = iteration.experiment.ilab_conf
        eps = ilab_conf.eps
        self.unsure = UncertainAnnotationQueries(iteration, ilab_conf.num_unsure, eps, 1-eps)
        self.malicious = ConfidentAnnotationQueries(iteration, 'malicious', ilab_conf.num_malicious, 1-eps, 1)
        self.benign = ConfidentAnnotationQueries(iteration, 'benign', ilab_conf.num_benign, 0, eps)

    def generateAnnotationQueries(self):
        self.unsure.run()
        self.malicious.run()
        self.benign.run()

    def annotateAuto(self):
        self.unsure.annotateAuto()
        self.malicious.annotateAuto()
        self.benign.annotateAuto()
