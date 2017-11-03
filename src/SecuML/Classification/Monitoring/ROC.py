## SecuML
## Copyright (C) 2016-2017  ANSSI
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
import numpy as np
from scipy import interp
from sklearn.metrics import roc_curve, auc

from SecuML.Tools import colors_tools

class ROC(object):

    def __init__(self, num_folds, conf):
        self.mean_tpr = 0.0
        self.mean_fpr = np.linspace(0, 1, 100)
        self.thresholds = None
        self.fig, (self.ax1) = plt.subplots(1, 1)
        self.probabilist_model = conf.probabilistModel()
        self.num_folds = num_folds

    def addFold(self, fold_id, true_labels, predicted_proba, predicted_scores):
        if len(true_labels) == 0:
            return
        if self.probabilist_model:
            scores = predicted_proba
        else:
            scores = predicted_scores
        fpr, tpr, thresholds = roc_curve(true_labels, scores)
        self.mean_tpr += interp(self.mean_fpr, fpr, tpr)
        self.thresholds = interp(self.mean_fpr, fpr, thresholds)
        self.mean_tpr[0] = 0.0
        self.thresholds[0] = 1.0
        self.thresholds[-1] = 0.0
        roc_auc = auc(fpr, tpr)
        if self.num_folds > 1:
            self.ax1.plot(fpr, tpr, lw = 1,
                    label = 'ROC fold %d (area = %0.2f)' % (fold_id, roc_auc))
        else:
            self.ax1.plot(fpr, tpr, lw = 3,
                    color = colors_tools.getLabelColor('all'),
                    label = 'ROC (area = %0.2f)' % (roc_auc))

    def display(self, directory):
        self.plot(directory + 'ROC.png')
        self.toCsv(directory + 'ROC.csv')

    def plot(self, output_file):
        self.ax1.plot([0, 1], [0, 1], '--', lw = 1,
                color = (0.6, 0.6, 0.6), label = 'Luck')
        if self.num_folds > 1:
            self.mean_tpr /= self.num_folds
            self.mean_tpr[-1] = 1.0
            mean_auc = auc(self.mean_fpr, self.mean_tpr)
            self.ax1.plot(self.mean_fpr, self.mean_tpr, 'k--',
                     label = 'Mean ROC (area = %0.2f)' % mean_auc, lw = 2)
        self.ax1.set_xlim([-0.05, 1.05])
        self.ax1.set_ylim([-0.05, 1.05])
        self.ax1.set_xlabel('False Positive Rate')
        self.ax1.set_ylabel('True Positive Rate')
        self.ax1.set_title('ROC Curve')
        self.ax1.legend(loc = 'lower right')
        self.fig.savefig(output_file)
        plt.close(self.fig)

    def toCsv(self, output_file):
        with open(output_file, 'w') as f:
            print >>f, 'Threshold,False Alarm Rate,Detection Rate'
            if self.thresholds is None: # The ROC is not defined
                return
            for i in range(len(self.mean_fpr)):
                print >>f, str(self.thresholds[i]) + ',' + str(self.mean_fpr[i]) + ',' + str(self.mean_tpr[i])
