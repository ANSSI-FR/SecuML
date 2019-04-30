# SecuML
# Copyright (C) 2016-2019  ANSSI
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

import csv
import matplotlib.pyplot as plt
import os
import os.path as path
import pandas as pd

from secuml.core.tools.plots.dataset import PlotDataset


class _ModelPerfEvolution(object):

    # kind: train, cv, test, or validation
    def __init__(self, iter_num, perf_indicators, multiclass, kind):
        self.iter_num = iter_num
        self.kind = kind
        self.perf_indicators = perf_indicators
        self.multiclass = multiclass

    def get_evol_file(self, evolution_dir):
        filename = '_'.join([self.kind, 'perf_monitoring.csv'])
        return path.join(evolution_dir, filename)

    def generate(self):
        return

    def export(self, monitoring_dir, evolution_dir):
        evolution_file = self.get_evol_file(evolution_dir)
        self.display_csv_line(evolution_file)
        self.plot_evolution(evolution_file, monitoring_dir)

    def display_csv_line(self, evolution_file):
        if self.iter_num == 1:
            self.display_csv_header(evolution_file)
        with open(evolution_file, 'a') as f:
            v = [self.iter_num]
            v.extend(self.perf_indicators.get_csv_line())
            csv_writer = csv.writer(f)
            csv_writer.writerow(v)

    def display_csv_header(self, evolution_file):
        with open(evolution_file, 'w') as f:
            header = ['iteration']
            header.extend(self.perf_indicators.get_csv_header())
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)

    def load_evolution(self, evolution_file):
        with open(evolution_file, 'r') as f:
            data = pd.read_csv(f, header=0, index_col=0)
            return data

    def plot_evolution(self, evolution_file, monitoring_dir):
        data = self.load_evolution(evolution_file)
        if self.multiclass:
            self.plot_perf_evolution(['accuracy'], 'accuracy', data,
                                     monitoring_dir)
            # self.plot_perf_evolution(['f1-micro', 'f1-macro'],
            #                           'f_micro_macro', data, monitoring_dir)
        else:
            self.plot_perf_evolution(['auc'], 'auc', data, monitoring_dir)
            # self.plot_perf_evolution(['fscore', 'precision', 'recall'],
            #                          'fscore', data, monitoring_dir)

    def plot_perf_evolution(self, estimators, output_filename, data,
                            output_dir):
        iterations = list(range(1, self.iter_num + 1))
        plt.clf()
        for estimator in estimators:
            plot = PlotDataset(data[estimator].values, estimator)
            plt.plot(iterations, plot.values, label=plot.label,
                     color=plot.color, linewidth=plot.linewidth,
                     marker=plot.marker)
        plt.ylim(0, 1)
        plt.xlabel('Iteration')
        plt.ylabel('Performance')
        lgd = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3,
                         mode='expand', borderaxespad=0., fontsize='large')
        filename = path.join(output_dir, '%s.png' % self.kind)
        plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()


class ModelPerfEvolution(object):

    def __init__(self, iter_num, diadem_exp, with_validation):
        self.iter_num = iter_num
        train_exp = diadem_exp.get_train_exp()
        train_detect_exp = diadem_exp.get_detection_exp('train')
        detect_exp = diadem_exp.get_detection_exp('test')
        kinds = {}
        kinds['train'] = train_detect_exp.monitoring
        if train_exp.monitoring.cv_monitoring is not None:
            kinds['cv'] = train_exp.monitoring.cv_monitoring.detect_monitoring
        if detect_exp.monitoring.has_ground_truth:
            kinds['test'] = detect_exp.monitoring
        if with_validation:
            validation_exp = diadem_exp.get_detection_exp('validation')
            if validation_exp.monitoring.has_ground_truth:
                kinds['validation'] = validation_exp.monitoring
        self.monitorings = {}
        multiclass = train_exp.exp_conf.core_conf.multiclass
        for k, diadem_monitoring in kinds.items():
            perf_indicators = diadem_monitoring.performance.perf_indicators
            self.monitorings[k] = _ModelPerfEvolution(iter_num,
                                                      perf_indicators,
                                                      multiclass, k)

    def generate(self):
        for _, monitoring in self.monitorings.items():
            monitoring.generate()

    def export(self, monitoring_dir, evolution_dir):
        monitoring_dir, evolution_dir = self._get_output_dirs(monitoring_dir,
                                                              evolution_dir)
        for _, monitoring in self.monitorings.items():
            monitoring.export(monitoring_dir, evolution_dir)

    def _get_output_dirs(self, iteration_dir, al_dir):
        monitoring_dir = self._get_monitoring_dir(iteration_dir)
        evolution_dir = self._get_evoluation_dir(al_dir)
        return monitoring_dir, evolution_dir

    def _get_monitoring_dir(self, iteration_dir):
        monitoring_dir = path.join(iteration_dir, 'model_perf')
        os.makedirs(monitoring_dir)
        return monitoring_dir

    def _get_evoluation_dir(self, al_dir):
        evolution_dir = path.join(al_dir, 'model_perf')
        if self.iter_num == 1:
            os.makedirs(evolution_dir)
        return evolution_dir
