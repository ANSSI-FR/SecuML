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

import copy

class LabelStats(object):

    def  __init__(self):
        self.labels = None
        self.annotations = None
        self.errors = None

    def addLabelsStats(self, label_stats):
        self.labels += label_stats.labels
        self.annotations += label_stats.annotations
        self.errors += label_stats.errors

    def getMaxValue(self):
        return max(self.labels, self.annotations, self.errors)

    def vectorRepresentation(self):
        return [self.annotations, self.labels, self.errors]

    def vectorHeader(self):
        return ['annotations', 'labels', 'errors']

class LabelsStats(object):

    def  __init__(self):
        self.stats = {}
        for l in ['global', 'malicious', 'benign']:
            self.stats[l] = LabelStats()

    def loadStats(self, labels_monitoring, unlabeled = False):
        for l in ['malicious', 'benign']:
            labels_monitoring.generateLabelMonitoring(l,
                    unlabeled = unlabeled)
        self.stats['global'] = copy.deepcopy(self.stats['benign'])
        self.stats['global'].addLabelsStats(self.stats['malicious'])

    def vectorRepresentation(self):
        v = []
        for l in ['global', 'malicious', 'benign']:
            v += self.stats[l].vectorRepresentation()
        return v

    def vectorHeader(self):
        v = []
        for l in ['global', 'malicious', 'benign']:
            header = self.stats[l].vectorHeader()
            header = [x + '_' + l for x in header]
            v += header
        return v
