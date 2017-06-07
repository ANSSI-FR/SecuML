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

from SecuML.Plots.PlotDataset import PlotDataset
from SecuML.Tools import dir_tools

class TrainTestValidationPerformanceMonitoring(object):

    def __init__(self, monitoring, model_name, train_test_validation):
        self.monitoring = monitoring
        self.model_name = model_name
        self.train_test_validation = train_test_validation
        self.setIsMulticlassModel()
        self.setOutputDirectory()
        self.setEvolutionFileName()
        self.setPerfIndicators()

    def setIsMulticlassModel(self):
        train_test = self.monitoring.iteration.train_test_validation
        model_conf = train_test.models[self.model_name].conf
        self.multiclass = model_conf.families_supervision

    def setOutputDirectory(self):
        self.output_directory  = self.monitoring.iteration_dir
        self.output_directory += 'models_performance/'

    def setEvolutionFileName(self):
        self.evolution_file  = self.monitoring.AL_directory
        self.evolution_file += 'models_performance/'
        self.evolution_file += self.model_name + '_'
        self.evolution_file += self.train_test_validation
        self.evolution_file += '_monitoring.csv'

    def setPerfIndicators(self):
        model = self.monitoring.iteration.train_test_validation.models[self.model_name]
        if self.train_test_validation == 'train':
            monitoring = model.training_monitoring
        elif self.train_test_validation == 'cv':
            monitoring = model.cv_monitoring
        elif self.train_test_validation == 'test':
            monitoring = model.testing_monitoring
        elif self.train_test_validation == 'validation':
            monitoring = model.validation_monitoring
        else:
            raise ValueError('Invalid value for train_test_validation, got %s' % self.train_test_validation)
        self.perf_indicators = monitoring.performance_monitoring.perf_indicators

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
        with open(self.evolution_file, 'a') as f:
            v = []
            v.append(self.monitoring.iteration_number)
            v += self.perf_indicators.getCsvLine()
            print >>f, ','.join(map(str, v))

    def displayCsvHeader(self):
        with open(self.evolution_file, 'w') as f:
            header  = ['iteration']
            header += self.perf_indicators.getCsvHeader()
            print >>f, ','.join(header)

    ##########################
    ## Evolution Monitoring ##
    ##########################

    def loadEvolutionMonitoring(self):
        with open(self.evolution_file, 'r') as f:
            self.data = pd.read_csv(f, header = 0, index_col = 0)

    def plotEvolutionMonitoring(self):
        if self.multiclass:
            self.plotPerfEvolution(['accuracy'], 'accuracy')
            self.plotPerfEvolution(['f1-micro', 'f1-macro'], 'f_micro_macro')
        else:
            self.plotPerfEvolution(['auc'], 'auc')
            self.plotPerfEvolution(['fscore', 'precision', 'recall'], 'fscore')

    def plotPerfEvolution(self, estimators, output_filename):
        iterations = range(self.monitoring.iteration_number)
        plt.clf()
        for estimator in estimators:
            plot = PlotDataset(self.data[estimator], estimator)
            plt.plot(iterations, plot.values,
                    label = plot.label,
                    color = plot.color,
                    linewidth = plot.linewidth, marker = plot.marker)
        plt.ylim(0, 1)
        plt.xlabel('Iteration')
        plt.ylabel('Performance')
        lgd = plt.legend(bbox_to_anchor = (0., 1.02, 1., .102), loc = 3,
                ncol = 3, mode = 'expand', borderaxespad = 0.,
                fontsize = 'large')
        filename = self.outputFilename(output_filename, 'png')
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()

    def outputFilename(self, name, extension):
        filename  = self.output_directory
        filename += self.model_name + '_'
        filename += self.train_test_validation + '_'
        filename += name + '_monitoring.' + extension
        return filename

class ModelPerformanceMonitoring(object):

    def __init__(self, monitoring, model_name, validation_monitoring):
        self.monitorings = {}
        train_test_validation = ['train', 'cv']
        model = monitoring.iteration.train_test_validation.models[model_name]
        if model.testing_monitoring.has_true_labels:
            train_test_validation.append('test')
        if validation_monitoring:
            train_test_validation.append('validation')
        for k in train_test_validation:
            self.monitorings[k] = TrainTestValidationPerformanceMonitoring(
                    monitoring, model_name, k)

    def iterationMonitoring(self):
        for kind, monitoring in self.monitorings.iteritems():
            monitoring.iterationMonitoring()

    def evolutionMonitoring(self):
        for kind, monitoring in self.monitorings.iteritems():
            monitoring.evolutionMonitoring()

class ModelsPerformanceMonitoring(object):

    def __init__(self, monitoring, validation_monitoring):
        self.createOutputDirectories(monitoring)
        self.models_monitoring = {}
        for kind, conf in monitoring.experiment.conf.models_conf.iteritems():
            self.models_monitoring[kind] = ModelPerformanceMonitoring(monitoring, kind, validation_monitoring)

    def createOutputDirectories(self, monitoring):
        output_directory  = monitoring.iteration_dir
        output_directory += 'models_performance/'
        dir_tools.createDirectory(output_directory)
        if monitoring.iteration_number == 1:
            output_directory  = monitoring.AL_directory
            output_directory += 'models_performance/'
            dir_tools.createDirectory(output_directory)

    def generateMonitoring(self):
        self.iterationMonitoring()
        self.evolutionMonitoring()

    def iterationMonitoring(self):
        for kind, monitoring in self.models_monitoring.iteritems():
            monitoring.iterationMonitoring()

    def evolutionMonitoring(self):
        for kind, monitoring in self.models_monitoring.iteritems():
            monitoring.evolutionMonitoring()
