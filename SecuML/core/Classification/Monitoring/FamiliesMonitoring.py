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

from decimal import Decimal
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interp
from sklearn.neighbors import KernelDensity
import os.path as path

from SecuML.core.Data import labels_tools
from SecuML.core.Tools import colors_tools

# The families monitoring is performed only if there are
# fewer than 150,000 instances.


class FamiliesMonitoring(object):

    def __init__(self, datasets, train_test, cv):
        self.datasets = datasets
        self.train_test = train_test
        self.cv = cv
        self.num_instances = 0
        self.all_predictions = []
        self.initFamiliesDict()

    def initFamiliesDict(self):
        self.families = {}
        for label in [labels_tools.BENIGN, labels_tools.MALICIOUS]:
            self.families[label] = {}

    def addFold(self, fold_id, predictions):
        self.num_instances += predictions.numInstances()
        if self.num_instances > 150000:
            return
        if len(self.all_predictions) == 0:
            self.all_predictions = list(predictions.predicted_proba)
        else:
            self.all_predictions += list(predictions.predicted_proba)
        annotations = self.getFoldAnnotations(fold_id)
        for i in range(predictions.numInstances()):
            label = labels_tools.labelBooleanToString(annotations.labels[i])
            family = annotations.families[i]
            proba = predictions.predicted_proba[i]
            if family not in self.families[label]:
                self.families[label][family] = []
            self.families[label][family].append(proba)

    def getFoldAnnotations(self, fold_id):
        dataset = self.datasets
        if self.cv:
            dataset = self.datasets.datasets[fold_id]
        if self.train_test == 'train':
            return dataset.train_instances.annotations
        elif self.train_test == 'test':
            return dataset.test_instances.annotations
        elif self.train_test == 'validation':
            return dataset.validation_instances.annotations

    def finalComputations(self):
        if self.num_instances < 150000:
            self.all_predictions = sorted(self.all_predictions)
            self.computeFpFn()

    def computeFpFn(self):
        thresholds = sorted(list(
            set([float(round(Decimal(x), 3)) for x in self.all_predictions] + [0.0, 1.0])))
        # Detection Rates
        malicious_families = self.families[labels_tools.MALICIOUS]
        self.detection_rates = pd.DataFrame(
            np.zeros((len(thresholds), len(malicious_families) + 1)),
            index=thresholds,
            columns=list(malicious_families.keys()) + ['Mean'])
        for family in list(malicious_families.keys()):
            predictions = sorted(malicious_families[family])
            num_predictions = len(predictions)
            predictions_u = sorted(list(set(predictions)))
            f_thresholds = [
                0.0] + [(t + s) / 2 for s, t in zip(predictions_u[:-1], predictions_u[1:])] + [1.0]
            perf = np.array([0] * len(f_thresholds))
            index = 0
            for p in predictions:
                while f_thresholds[index] < p:
                    index += 1
                perf[index:] += 1
            perf = 1 - perf / num_predictions
            perf = interp(thresholds, f_thresholds, perf)
            self.detection_rates[family] = perf
        self.detection_rates['Mean'] = self.detection_rates.loc[:, list(
            malicious_families.keys())].mean(axis=1)
        # False Alarm Rates
        benign_families = self.families[labels_tools.BENIGN]
        self.false_alarm_rates = pd.DataFrame(
            np.zeros((len(thresholds), len(benign_families) + 1)),
            index=thresholds,
            columns=list(benign_families.keys()) + ['Mean'])
        for family in list(benign_families.keys()):
            predictions = sorted(benign_families[family])
            num_predictions = len(predictions)
            predictions_u = sorted(list(set(predictions)))
            f_thresholds = [
                0.0] + [(t + s) / 2 for s, t in zip(predictions_u[:-1], predictions_u[1:])] + [1.0]
            perf = np.array([0] * len(f_thresholds))
            index = 0
            for p in predictions:
                while f_thresholds[index] < p:
                    index += 1
                perf[index:] += 1
            perf = 1 - perf / num_predictions
            perf = interp(thresholds, f_thresholds, perf)
            self.false_alarm_rates[family] = perf
        self.false_alarm_rates['Mean'] = self.false_alarm_rates.loc[:, list(
            benign_families.keys())].mean(axis=1)

    def display(self, directory):
        if self.num_instances < 150000:
            self.displayFpFnThresholds(directory)
            # Density plots
            # They are computed only if there are fewer than 150.000 instances
            # self.displayFamiliesDistribution(directory)

    def displayFpFnThresholds(self, directory):
        with open(path.join(directory, 'tp_families_thresholds.csv'), 'w') as f:
            self.detection_rates.to_csv(f, index_label='Threshold')
        with open(path.join(directory, 'fp_families_thresholds.csv'), 'w') as f:
            self.false_alarm_rates.to_csv(f, index_label='Threshold')

    def displayFamiliesDistribution(self, directory, label=None):
        if label is None:
            self.displayFamiliesDistribution(directory,
                                             label=labels_tools.MALICIOUS)
            self.displayFamiliesDistribution(directory,
                                             label=labels_tools.MALICIOUS)
            return
        families = self.families[labels_tools.labelBooleanToString(label)]
        bandwidth = 0.1
        num_points = 50
        eps = 0.00001
        kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth)
        fig, (ax) = plt.subplots(1, 1)
        i = 0
        for family in families:
            predictions = families[family]
            predictions_np = np.asarray(predictions)
            if i % 3 == 0:
                linestyle = 'solid'
            elif i % 3 == 1:
                linestyle = 'dashed'
            if i % 3 == 2:
                linestyle = 'dotted'
            linewidth = 2
            if np.var(predictions_np) < eps:
                linewidth = 4
                mean = np.mean(predictions_np)
                x = np.arange(0, 1, 0.1)
                x = np.sort(np.append(x, [mean, mean - eps, mean + eps]))
                density = [1 if v == mean else 0 for v in x]
            else:
                density_predictions = [[x] for x in predictions_np]
                kde.fit(density_predictions)
                # Computes the x axis
                p_max = np.amax(predictions_np)
                p_min = np.amin(predictions_np)
                delta = p_max - p_min
                density_delta = 1.1 * delta
                x = np.arange(0, 1, density_delta / num_points)
                x_density = [[y] for y in x]
                # kde.score_samples returns the 'log' of the density
                log_density = kde.score_samples(x_density).tolist()
                density = list(map(math.exp, log_density))
            ax.plot(x, density, label=family,
                    linewidth=linewidth, linestyle=linestyle)
            fig_f, (ax_f) = plt.subplots(1, 1)
            ax_f.plot(x, density, linewidth=4,
                      color=colors_tools.getLabelColor(label))
            ax_f.set_title(family)
            ax_f.set_xlabel('P(Malicious)')
            ax_f.set_ylabel('Density')
            filename = label + '_family_' + family + '_prediction_distributions.png'
            fig_f.savefig(path.join(directory, filename))
            plt.close(fig_f)
            i += 1
        ax.legend(bbox_to_anchor=(0., 0.95, 1., .102), loc=3,
                  ncol=5, mode='expand', borderaxespad=0.,
                  fontsize='xx-small')
        ax.set_xlabel('P(Malicious)')
        ax.set_ylabel('Density')
        filename = label + '_families_prediction_distributions.png'
        fig.savefig(path.join(directory, filename))
        plt.close(fig)
