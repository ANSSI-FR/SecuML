## SecuML
## Copyright (C) 2017  ANSSI
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

import numpy as np
import scipy
from sklearn.preprocessing import StandardScaler
import time
import warnings

from SecuML.Classification.Classifier import Classifier
from SecuML.Classification.Classifier import Predictions
from SecuML.Classification.Monitoring.TestingMonitoring import TestingMonitoring
from SecuML.Classification.Monitoring.TrainingMonitoring import TrainingMonitoring

# Works when no labeled instances are provided.

class Sssvdd(Classifier):

    def __init__(self, experiment, datasets, cv_monitoring = False):
        Classifier.__init__(self, experiment, datasets, cv_monitoring = cv_monitoring)
        self.scaler = None
        self.c      = None
        self.r      = None
        # Parameters
        self.nu_L  = 1.
        self.nu_U  = 1.
        self.kappa = 1.
        self.checkCvMonitoring()

    def checkCvMonitoring(self):
        if self.cv_monitoring:
            warnings.warn('Sssvdd does not support cv_monitoring.\n')
            self.cv_monitoring = None

    def training(self):
        self.training_execution_time = 0

        # Scaling and training
        start = time.time()
        self.scaler = StandardScaler()
        training_features = self.datasets.train_instances.getFeatures()
        self.scaler.fit(training_features)

        unlabeled_instances = self.datasets.train_instances.getUnlabeledInstances()
        unlabeled_features  = np.array(self.scaler.transform(
            unlabeled_instances.getFeatures()))
        labeled_instances   = self.datasets.train_instances.getLabeledInstances()
        if labeled_instances.numInstances() > 0:
            labeled_features = np.array(self.scaler.transform(
                labeled_instances.getFeatures()))
        else:
            labeled_features = np.array(labeled_instances.getFeatures())
        labels = np.array([-1. if x else 1. for x in labeled_instances.getLabels()])

        num_labeled_instances   = labeled_instances.numInstances()
        num_unlabeled_instances = unlabeled_instances.numInstances()

        # To avoid numerical instability
        self.nu_L /= num_labeled_instances
        self.nu_U /= num_unlabeled_instances

        x_init = generateXinit(unlabeled_features, labeled_features,
                               labeled_instances.getLabels())
        optim_res = scipy.optimize.fmin_bfgs(
                objective,
                x_init,
                fprime = gradient,
                args = (unlabeled_features, labeled_features, labels, self.kappa,
                        self.nu_U, self.nu_L))
        self.r, _, self.c = getValues(optim_res)

        self.training_execution_time = time.time() - start

        self.training_predictions = self.applyPipeline(labeled_instances.getFeatures())
        self.coefs = [0] * len(self.datasets.getFeaturesNames())

    # Training monitoring
    # The model is trained on all the available data (labeled and unlabeled)
    # but the training monitoring is performed only on the labeled instances
    def exportTraining(self, output_directory):
        self.training_monitoring = TrainingMonitoring(self.conf,
                self.datasets.getFeaturesNames(), monitoring_type = 'train')
        labeled_instances = self.datasets.train_instances.getLabeledInstances()
        self.training_monitoring.addFold(0,
                labeled_instances.getLabels(),
                labeled_instances.getFamilies(), labeled_instances.getIds(),
                self.training_predictions, self.coefs)
        self.training_monitoring.display(output_directory)

    def applyPipeline(self, features):
        preprocessed_features = self.scaler.transform(features)
        predicted_scores    = np.apply_along_axis(predictScore, 1,
                                                  preprocessed_features,
                                                  self.c, self.r)
        predicted_labels    = predicted_scores > 0
        predicted_proba     = None
        predicted_proba_all = None
        return Predictions(predicted_proba_all, predicted_proba,
                           predicted_labels, predicted_scores)

    def dumpModel(self):
        return

def predictLabel(x, center, r):
    return predictScore(x, center, r) > 0

def predictScore(x, center, r):
    return squareDistanceToCenter(x, center) - pow(r, 2)

def objective(x, unlabeled_features, labeled_features, labels, kappa, nu_U, nu_L):
    R, gamma, c = getValues(x)

    # Unlabeled sum
    num_unlabeled_instances = unlabeled_features.shape[0]
    sum_U = 0
    for i in range(num_unlabeled_instances):
        sum_U += l(R*R - squareDistanceToCenter(unlabeled_features[i, :], c))

    # Labeled sum
    sum_L = 0
    num_labeled_instances = labeled_features.shape[0]
    if num_labeled_instances > 0:
        for i in range(num_labeled_instances):
            sum_L += l(labels[i] * (R*R - squareDistanceToCenter(labeled_features[i, :], c)) - gamma)

    obj  = R*R
    obj -= kappa*gamma
    obj += nu_U * sum_U
    obj += nu_L * sum_L
    return obj


def distanceToCenter(x_i, center):
    return np.linalg.norm(x_i - center)

def squareDistanceToCenter(x_i, center):
    return np.dot(x_i - center, x_i - center)

def partial_derivatives_R(x_i, x):
    R, _, c = getValues(x)
    return 2 * R * l_prime(R*R - squareDistanceToCenter(x_i, c))

def partial_derivatives_c(x_i, x):
    R, _, c = getValues(x)
    return 2 * (x_i - c) * l_prime(R*R - squareDistanceToCenter(x_i, c))

def partial_derivatives_R_star(x_i, y_i, x):
    R, gamma, c = getValues(x)
    return 2 * y_i * R * l_prime(y_i * (R*R - squareDistanceToCenter(x_i, c)) - gamma)

def partial_derivatives_gamma_star(x_i, y_i, x):
    R, gamma, c = getValues(x)
    return -l_prime(y_i * (R*R - squareDistanceToCenter(x_i, c)) - gamma)

def partial_derivatives_c_star(x_i, y_i, x):
    R, gamma, c = getValues(x)
    return 2 * y_i * (x_i - c) * l_prime(y_i * (R*R - squareDistanceToCenter(x_i, c)) - gamma)

def gradient_r(x, unlabeled_features, labeled_features, labels, nu_U, nu_L):
    R, _, _ = getValues(x)

    # Unlabeled sum
    num_unlabeled_instances = unlabeled_features.shape[0]
    sum_U = 0
    for i in range(num_unlabeled_instances):
        sum_U += partial_derivatives_R(unlabeled_features[i, :], x)

    # Labeled sum
    sum_L = 0
    num_labeled_instances = labeled_features.shape[0]
    if num_labeled_instances > 0:
        for i in range(num_labeled_instances):
            sum_L += partial_derivatives_R_star(labeled_features[i, :], labels[i], x)

    return 2*R + nu_U*sum_U + nu_L*sum_L

def gradient_gamma(x, labeled_features, labels, kappa, nu_L):
    # Labeled sum
    sum_L = 0
    num_labeled_instances = labeled_features.shape[0]
    if num_labeled_instances > 0:
        for i in range(num_labeled_instances):
            sum_L += partial_derivatives_gamma_star(labeled_features[i, :], labels[i], x)

    return -kappa + nu_L*sum_L

def gradient_c(x, unlabeled_features, labeled_features, labels, nu_U, nu_L):
    # Unlabeled sum
    num_unlabeled_instances = unlabeled_features.shape[0]
    sum_U = 0
    for i in range(num_unlabeled_instances):
        sum_U += partial_derivatives_c(unlabeled_features[i, :], x)

    # Labeled sum
    sum_L = 0
    num_labeled_instances = labeled_features.shape[0]
    if num_labeled_instances > 0:
        for i in range(num_labeled_instances):
            sum_L += partial_derivatives_c_star(labeled_features[i, :], labels[i], x)

    res = nu_U*sum_U + nu_L*sum_L
    return res

def gradient(x, unlabeled_features, labeled_features, labels, kappa, nu_U, nu_L):
    g_r = gradient_r(x, unlabeled_features, labeled_features, labels, nu_U, nu_L)
    g_gamma = gradient_gamma(x, labeled_features, labels, kappa, nu_L)
    g = np.concatenate((np.array([g_r, g_gamma]),
                        gradient_c(x, unlabeled_features, labeled_features,
                                   labels, nu_U, nu_L)))
    return g

# the features have been scaled before
# compute the center and the radius of the benign and unlabeled instances
# gamma is set to 1
def generateXinit(unlabeled_features, labeled_features, labels):
    gamma_init = 1.
    c_init, r_init = benignInstancesCenterRadius(unlabeled_features,
                                                 labeled_features, labels)
    return np.array([r_init, gamma_init] + list(c_init))

def benignInstancesCenterRadius(unlabeled_features, labeled_features, labels):
    benign_features = labeled_features[-np.array(labels)]
    benign_features = np.concatenate((benign_features, unlabeled_features))
    center = np.mean(benign_features, axis = 0)
    radius = np.mean(np.apply_along_axis(distanceToCenter, 1, benign_features, center))
    return center, radius

def l(t):
    delta = 0.
    eps   = 0.5
    if t <= delta - eps:
        return delta - t
    elif delta - eps <= t and t <= delta + eps:
        return pow(delta + eps - t, 2) / (4.*eps)
    else:
        return 0

def l_prime(t):
    delta = 0.
    eps   = 0.5
    if t <= delta - eps:
        return -1.
    elif delta - eps <= t and t <= delta + eps:
        return -0.5 * ((delta-t) / eps + 1.)
    else:
        return 0

def getValues(x):
    R     = x[0]
    gamma = x[1]
    c     = x[2:]
    return R, gamma, c
