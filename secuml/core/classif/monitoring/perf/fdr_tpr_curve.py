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
import numpy as np
from scipy import interp
from sklearn.metrics import precision_recall_curve
import os.path as path

from secuml.core.tools.color import get_label_color


def interp_recall(ground_truth, scores, precision_sample):
    precision, recall, thresholds = precision_recall_curve(ground_truth,
                                                           scores)
    # precision_recall_curve do not return vectors of the same length.
    # len(thresholds) = n, with len(precision) = len(recall) = n+1
    thresholds = np.append(thresholds, 1)
    # Add corner cases
    thresholds = np.append(0, thresholds)
    precision = np.append(sum(ground_truth) / len(ground_truth), precision)
    recall = np.append(1, recall)
    # Interpolation
    recall = interp(precision_sample, precision, recall)
    thresholds = interp(precision_sample, precision, thresholds)
    return recall, thresholds


class FdrTprCurve(object):

    def __init__(self, num_folds, probabilist):
        self.mean_recall = None
        self.mean_precision = np.linspace(0, 1, 101)
        self.thresholds = None
        self.fig, (self.ax1) = plt.subplots(1, 1)
        self.probabilist = probabilist
        self.num_folds = num_folds

    def add_fold(self, fold_id, predictions):
        if (predictions.num_instances() == 0 or
                sum(predictions.ground_truth) == 0):
            return
        if self.probabilist:
            scores = predictions.probas
        else:
            scores = predictions.scores
        recall, thresholds = interp_recall(predictions.ground_truth, scores,
                                           self.mean_precision)
        if self.mean_recall is None:
            self.mean_recall = recall
        else:
            self.mean_recall += recall
        if self.num_folds > 1:
            self.ax1.plot(1 - self.mean_precision, recall, lw=1,
                          label='FAR/DR fold %d' % (fold_id))
        else:
            self.ax1.plot(1 - self.mean_precision, recall, lw=3,
                          color=get_label_color('all'), label='FAR/DR')
        return 1 - self.mean_precision, recall

    def display(self, directory):
        self.plot(path.join(directory, 'false_discovery_recall_curve.png'))
        self.to_csv(path.join(directory, 'false_discovery_recall_curve.csv'))

    def plot(self, output_file):
        if self.num_folds > 1:
            self.mean_recall /= self.num_folds
            self.ax1.plot(1 - self.mean_precision,
                          self.mean_recall,
                          'k--',
                          label='Mean FAR/DR',
                          lw=2)
        self.ax1.set_xlim([-0.05, 1.05])
        self.ax1.set_ylim([-0.05, 1.05])
        self.ax1.set_xlabel('False Alarm Rate (1 - Precision)')
        self.ax1.set_ylabel('Detection Rate (Recall)')
        self.ax1.set_title('False Alarm Rate / Detection Rate Curve')
        self.ax1.legend(loc='lower right')
        self.fig.savefig(output_file)
        plt.close(self.fig)

    def to_csv(self, output_file):
        with open(output_file, 'w') as f:
            csv_writer = csv.writer(f)
            header = ['Threshold', 'Precision', 'Recall']
            csv_writer.writerow(header)
            if self.thresholds is None:  # The curve is not defined
                return
            for i in range(len(self.mean_precision)):
                row = [self.thresholds[i], self.mean_precision[i],
                       self.mean_recall[i]]
                csv_writer.writerow(row)
