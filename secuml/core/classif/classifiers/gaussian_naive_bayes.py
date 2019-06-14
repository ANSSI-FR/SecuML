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

import numpy as np
import scipy.stats
from sklearn import naive_bayes
from sklearn.preprocessing import StandardScaler

from . import SupervisedClassifier


class _GaussianNaiveBayes(naive_bayes.GaussianNB):

    # FIXME: a more efficient implementation should be provided.
    def predict_from_probas(self, X, probas):
        return self.predict(X)


class GaussianNaiveBayes(SupervisedClassifier):

    def _get_pipeline(self):
        return [('scaler', StandardScaler()),
                ('model', _GaussianNaiveBayes())]

    def log_likelihood(self, features, label):
        all_theta = self.pipeline.named_steps['model'].theta_
        all_sigma = self.pipeline.named_steps['model'].sigma_
        scaled_features = self.pipeline.named_steps['scaler'].transform(
            features)
        label_index = np.where(self.class_labels == label)[0]
        theta = all_theta[label_index, :][0]
        sigma = all_sigma[label_index, :][0]
        probas = scipy.stats.norm(theta, sigma).pdf(scaled_features)
        log_likelihoods = np.sum(
            np.log(np.maximum(probas, np.finfo(float).eps)), axis=1)
        return log_likelihoods
