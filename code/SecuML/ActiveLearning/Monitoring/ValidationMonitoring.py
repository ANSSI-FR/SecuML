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

import matplotlib.pyplot as plt
import pandas as pd

from SecuML.Tools import colors_tools

class ValidationMonitoring(object):

    def __init__(self, monitoring):
        self.monitoring = monitoring
        self.evolution_file  = self.monitoring.AL_directory
        self.evolution_file += 'validation_monitoring.csv'
        self.multilabel_validation = self.monitoring.iteration.train_test_validation.multilabel_classifier is not None

    def iterationMonitoring(self):
        self.displayCsvLine()

    def evolutionMonitoring(self):
        self.loadEvolutionMonitoring()
        self.plotEvolutionMonitoring()

    ##########################
    ## Iteration Monitoring ##
    ##########################

    def displayCsvLine(self):
        if self.monitoring.iteration_number == 1:
            self.displayCsvHeader()
        train_test = self.monitoring.iteration.train_test_validation
        with open(self.evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iteration_number)
            # Binary validation
            validation_monitoring = train_test.binary_classifier.validation_monitoring
            validation_perf = validation_monitoring.performance_monitoring.perf_indicators
            v.append(validation_perf.getAuc())
            v.append(validation_perf.getFscore())
            v.append(validation_perf.getPrecision())
            v.append(validation_perf.getRecall())
            # Multi-label validation
            if self.multilabel_validation:
                validation_monitoring = train_test.multilabel_classifier.validation_monitoring
                validation_perf = validation_monitoring.performance_monitoring.perf_indicators
                v.append(validation_perf.f1_micro_mean)
                v.append(validation_perf.f1_macro_mean)
            print >>f, ','.join(map(str, v))

    def displayCsvHeader(self):
        with open(self.evolution_file, 'w') as f:
            header  = ['iteration']
            header.append('auc')
            header.append('fscore')
            header.append('precision')
            header.append('recall')
            if self.multilabel_validation:
                header.append('f1-micro')
                header.append('f1-macro')
            print >>f, ','.join(header)

    ##########################
    ## Evolution Monitoring ##
    ##########################

    def loadEvolutionMonitoring(self):
        with open(self.evolution_file, 'r') as f:
            self.data = pd.read_csv(f, header = 0, index_col = 0)

    def plotEvolutionMonitoring(self):
        self.plotAucEvolution()
        self.plotFscoreEvolution()
        if self.multilabel_validation:
            self.plotMultilabelEvolution()

    def plotAucEvolution(self):
        iterations = range(self.monitoring.iteration_number)
        plt.clf()
        plt.plot(iterations, self.data.loc[:]['auc'],
                label = 'auc',
                color = colors_tools.getLabelColor('all'), linewidth = 3, marker = 'o')
        plt.ylim(0, 1)
        plt.xlabel('Iteration')
        plt.ylabel('Performance')
        lgd = plt.legend(bbox_to_anchor = (0., 1.02, 1., .102), loc = 3,
                ncol = 1, mode = 'expand', borderaxespad = 0.,
                fontsize = 'x-large')
        filename  = self.monitoring.iteration_dir
        filename += 'auc_validation_monitoring.png'
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()

    def plotFscoreEvolution(self):
        iterations = range(self.monitoring.iteration_number)
        plt.clf()
        for estimator in ['fscore', 'precision', 'recall']:
            plt.plot(iterations, self.data.loc[:][estimator],
                    label = estimator,
                    linewidth = 3, marker = 'o')
        plt.ylim(0, 1)
        plt.xlabel('Iteration')
        plt.ylabel('Performance')
        lgd = plt.legend(bbox_to_anchor = (0., 1.02, 1., .102), loc = 3,
                ncol = 3, mode = 'expand', borderaxespad = 0.,
                fontsize = 'x-large')
        filename  = self.monitoring.iteration_dir
        filename += 'fscore_validation_monitoring.png'
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()

    def plotMultilabelEvolution(self):
        iterations = range(self.monitoring.iteration_number)
        plt.clf()
        for estimator in ['f1-micro', 'f1-macro']:
            plt.plot(iterations, self.data.loc[:][estimator],
                    label = estimator,
                    linewidth = 3, marker = 'o')
        plt.ylim(0, 1)
        plt.xlabel('Iteration')
        plt.ylabel('Performance')
        lgd = plt.legend(bbox_to_anchor = (0., 1.02, 1., .102), loc = 3,
                ncol = 3, mode = 'expand', borderaxespad = 0.,
                fontsize = 'x-large')
        filename  = self.monitoring.iteration_dir
        filename += 'multilabel_validation_monitoring.png'
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()
