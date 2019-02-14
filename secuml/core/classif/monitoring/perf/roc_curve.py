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

import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy import interp
from sklearn.metrics import roc_curve, auc
import os.path as path

from secuml.core.tools.color import get_label_color


class RocCurve(object):

    def __init__(self, num_folds, probabilist):
        self.mean_tpr = None
        self.mean_fpr = np.linspace(0, 1, 101)
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
        fpr, tpr, thresholds = roc_curve(predictions.ground_truth, scores)
        # Add corner cases
        thresholds = np.append(1, thresholds)
        fpr = np.append(0, fpr)
        tpr = np.append(0, tpr)
        thresholds = np.append(thresholds, 0)
        fpr = np.append(fpr, 1)
        tpr = np.append(tpr, 1)
        if self.mean_tpr is None:
            self.mean_tpr = interp(self.mean_fpr, fpr, tpr)
        else:
            self.mean_tpr += interp(self.mean_fpr, fpr, tpr)
        self.thresholds = interp(self.mean_fpr, fpr, thresholds)
        roc_auc = auc(fpr, tpr)
        if self.num_folds > 1:
            self.ax1.plot(fpr, tpr, lw=1,
                          label='ROC fold %d (area = %0.2f)' % (fold_id,
                                                                roc_auc))
        else:
            self.ax1.plot(fpr, tpr, lw=3, color=get_label_color('all'),
                          label='ROC (area = %0.2f)' % (roc_auc))
        return fpr, tpr, roc_auc

    def display(self, directory):
        self.plot(path.join(directory, 'ROC.png'))
        self.to_csv(path.join(directory, 'ROC.csv'))

    def plot(self, output_file):
        self.ax1.plot([0, 1], [0, 1], '--', lw=1,
                      color=(0.6, 0.6, 0.6), label='Luck')
        if self.num_folds > 1:
            self.mean_tpr /= self.num_folds
            mean_auc = auc(self.mean_fpr, self.mean_tpr)
            self.ax1.plot(self.mean_fpr, self.mean_tpr, 'k--',
                          label='Mean ROC (area = %0.2f)' % mean_auc, lw=2)
        self.ax1.set_xlim([-0.05, 1.05])
        self.ax1.set_ylim([-0.05, 1.05])
        self.ax1.set_xlabel('False Positive Rate')
        self.ax1.set_ylabel('True Positive Rate (Detection Rate)')
        self.ax1.set_title('ROC Curve')
        self.ax1.legend(loc='lower right')
        self.fig.savefig(output_file)
        plt.close(self.fig)

    def to_csv(self, output_file):
        with open(output_file, 'w') as f:
            csv_writer = csv.writer(f)
            header = ['Threshold', 'False Alarm Rate', 'Detection Rate']
            csv_writer.writerow(header)
            if self.thresholds is None:  # The ROC is not defined
                return
            for i in range(len(self.mean_fpr)):
                row = [self.thresholds[i], self.mean_fpr[i], self.mean_tpr[i]]
                csv_writer.writerow(row)
