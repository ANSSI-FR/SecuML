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

class ValidationMonitoring(object):

    def __init__(self, monitoring):
        self.monitoring = monitoring
        self.evolution_file  = self.monitoring.AL_directory
        self.evolution_file += 'validation_monitoring.csv'
    
    def iterationMonitoring(self):
        self.displayCsvLine()

    def evolutionMonitoring(self):
        self.loadEvolutionMonitoring()
        self.plotEvolutionMonitoring()

    #############################
    #############################
    ##### Private functions #####
    #############################
    #############################

    ##########################
    ## Iteration Monitoring ##
    ##########################

    def displayCsvLine(self):
        exp = self.monitoring.iteration.experiment
        if self.monitoring.iteration_number == 1:
            self.displayCsvHeader()
        iteration = self.monitoring.iteration
        with open(self.evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iteration_number)
            validation_monitoring = iteration.train_test_validation.classifier.validation_monitoring
            validation_perf = validation_monitoring.performance_monitoring.perf_indicators
            v.append(validation_perf.getAuc())
            v.append(validation_perf.getFscore())
            v.append(validation_perf.getPrecision())
            v.append(validation_perf.getRecall())
            print >>f, ','.join(map(str, v))

    def displayCsvHeader(self):
        with open(self.evolution_file, 'w') as f:
            header  = ['iteration']
            header.append('auc')
            header.append('fscore')
            header.append('precision')
            header.append('recall')
            print >>f, ','.join(header)

    ##########################
    ## Evolution Monitoring ##
    ##########################

    def loadEvolutionMonitoring(self):
        with open(self.evolution_file, 'r') as f:
            self.data = pd.read_csv(f, header = 0, index_col = 0)
    
    def plotEvolutionMonitoring(self):
        iterations = range(self.monitoring.iteration_number)
        ## AUC
        plt.clf()
        plt.plot(iterations, self.data.loc[:]['auc'],
                label = 'auc',
                color = 'blue', linewidth = 4, marker = 'o')
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
        ## F-score
        plt.clf()
        for estimator in ['fscore', 'precision', 'recall']:
            plt.plot(iterations, self.data.loc[:][estimator],
                    label = estimator,
                    linewidth = 4, marker = 'o')
        plt.ylim(0, 1)
        plt.xlabel('Iteration')
        plt.ylabel('Performance')
        lgd = plt.legend(bbox_to_anchor = (0., 1.02, 1., .102), loc = 3,
                ncol = 1, mode = 'expand', borderaxespad = 0.,
                fontsize = 'x-large')
        filename  = self.monitoring.iteration_dir
        filename += 'fscore_validation_monitoring.png'
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()
    
    #def display(self, output_dir):
    #    plt.clf()
    #    plt.plot(self.iterations, self.fscore,
    #            label = 'fscore',
    #            color = 'red', linewidth = 2, marker = 'o')
    #    plt.plot(self.iterations, self.precision,
    #            label = 'precision',
    #            color = 'green', linewidth = 2, marker = 'o')
    #    plt.plot(self.iterations, self.recall,
    #            label = 'recall',
    #            color = 'blue', linewidth = 2, marker = 'o')
    #    plt.xlabel('Iteration')
    #    plt.ylabel('Performance')
    #    plt.legend()
    #    plt.savefig(output_dir + 'iteration_perf.png')
    #    plt.clf()
    #    plt.plot(self.num_annotations['global'], self.fscore,
    #            label = 'fscore',
    #            color = 'red', linewidth = 2, marker = 'o')
    #    plt.plot(self.num_annotations['global'], self.precision,
    #            label = 'precision',
    #            color = 'green', linewidth = 2, marker = 'o')
    #    plt.plot(self.num_annotations['global'], self.recall,
    #            label = 'recall',
    #            color = 'blue', linewidth = 2, marker = 'o')
    #    plt.xlabel('Num annotations')
    #    plt.ylabel('Performance')
    #    plt.legend()
    #    plt.savefig(output_dir + 'annotation_perf.png')
    #    plt.clf()
