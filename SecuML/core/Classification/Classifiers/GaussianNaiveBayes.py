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

import numpy as np
import scipy.stats
from sklearn import naive_bayes
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from SecuML.core.Classification.Classifier import Classifier


class GaussianNaiveBayes(Classifier):

    def createPipeline(self):
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', naive_bayes.GaussianNB())])

    def logLikelihood(self, features, label):
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
