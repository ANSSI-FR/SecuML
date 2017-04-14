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

from SecuML.Plots.BarPlot import BarPlot
from SecuML.Tools import colors_tools

class PredictionsBarplots(object):

    def __init__(self):
        self.ranges = [[] for i in range(10)]

    def addFold(self, instances_ids, predicted_proba, true_labels):
        for i, instance_id in enumerate(instances_ids):
            proba       = predicted_proba[i]
            if true_labels is not None:
                label = true_labels[i]
            else:
                label = None
            ## Prb if proba = 1
            if proba == 1:
                proba = 0.999999
            self.ranges[int(proba*10)].append(
                    {
                        'instance_id': instance_id,
                        'true_label': label})

    def display(self, directory):
        labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
        barplot = BarPlot(labels)
        barplot.addDataset(map(len, self.ranges), colors_tools.getLabelColor('all'), 'numInstances')
        filename = directory + 'predictions_barplot.json'
        with open(filename, 'w') as f:
            barplot.display(f)
        barplot = BarPlot(labels)
        malicious_ranges = map(
                lambda l: filter(lambda x: x['true_label'], l),
                self.ranges)
        benign_ranges = map(
                lambda l: filter(lambda x: not x['true_label'], l),
                self.ranges)
        barplot.addDataset(map(len, malicious_ranges),
                           colors_tools.getLabelColor('malicious'), 'malicious')
        barplot.addDataset(map(len, benign_ranges),
                           colors_tools.getLabelColor('benign'), 'benign')
        filename  = directory
        filename += 'predictions_barplot_labels.json'
        with open(filename, 'w') as f:
            barplot.display(f)
