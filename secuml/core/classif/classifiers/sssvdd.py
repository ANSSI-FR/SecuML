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
import scipy
from sklearn.preprocessing import StandardScaler
import time

from . import Classifier
from . import NoCvMonitoring
from secuml.core.data.predictions import Predictions


class Sssvdd(Classifier):

    def __init__(self, conf):
        Classifier.__init__(self, conf)
        self.scaler = None
        self.c = None
        self.r = None
        # Parameters
        self.nu_L = 1.
        self.nu_U = 1.
        self.kappa = 1.

    def _create_pipeline(self):
        self.pipeline = None

    def cv_monitoring(self, train_instances, cv_monitoring):
        raise NoCvMonitoring(self)

    def training(self, train_instances):
        exec_time = 0

        # Scaling and training
        start = time.time()
        self.scaler = StandardScaler()
        training_features = train_instances.features.get_values()
        self.scaler.fit(training_features)

        unlabeled_instances = train_instances.get_unlabeled_instances()
        if unlabeled_instances.num_instances() > 0:
            unlabeled_features = self.scaler.transform(
                unlabeled_instances.features.get_values())
        else:
            unlabeled_features = unlabeled_instances.features.get_values()
        labeled_instances = train_instances.get_annotated_instances()
        if labeled_instances.num_instances() > 0:
            labeled_features = self.scaler.transform(
                labeled_instances.features.get_values())
        else:
            labeled_features = labeled_instances.features.get_values()
        labels = np.array([-1. if x else 1.
                           for x in
                           labeled_instances.annotations.get_labels()])
        num_labeled_instances = labeled_instances.num_instances()
        num_unlabeled_instances = unlabeled_instances.num_instances()

        # To avoid numerical instability
        if num_labeled_instances > 0:
            self.nu_L /= num_labeled_instances
        if num_unlabeled_instances > 0:
            self.nu_U /= num_unlabeled_instances

        x_init = gen_x_init(unlabeled_features, labeled_features,
                            labeled_instances.annotations.get_labels())
        optim_res = scipy.optimize.fmin_bfgs(
            objective,
            x_init,
            fprime=gradient,
            args=(unlabeled_features, labeled_features, labels, self.kappa,
                  self.nu_U, self.nu_L),
            disp=False)  # not to display the convergence message
        self.r, _, self.c = get_values(optim_res)

        exec_time = time.time() - start

        train_predictions = self._get_predictions(labeled_instances)
        return train_predictions, exec_time

    def apply_pipeline(self, instances):
        num_instances = instances.num_instances()
        if num_instances == 0:
            return Predictions([], instances.ids, False)
        features = instances.features.get_values()
        preprocessed_features = self.scaler.transform(features)
        predicted_scores = np.apply_along_axis(predict_score, 1,
                                               preprocessed_features,
                                               self.c, self.r)
        predicted_labels = predicted_scores > 0
        return Predictions(predicted_labels, instances.ids, False,
                           scores=predicted_scores)


def predict_label(x, center, r):
    return predict_score(x, center, r) > 0


def predict_score(x, center, r):
    return square_distance_to_center(x, center) - pow(r, 2)


def objective(x, unlabeled_features, labeled_features, labels, kappa, nu_U,
              nu_L):
    R, gamma, c = get_values(x)
    # Unlabeled sum
    num_unlabeled_instances = unlabeled_features.shape[0]
    sum_U = 0
    for i in range(num_unlabeled_instances):
        sum_U += _l(R * R -
                    square_distance_to_center(unlabeled_features[i, :], c))
    # Labeled sum
    sum_L = 0
    num_labeled_instances = labeled_features.shape[0]
    if num_labeled_instances > 0:
        for i in range(num_labeled_instances):
            square_dist = square_distance_to_center(labeled_features[i, :], c)
            sum_L += _l(labels[i] * (R * R - square_dist) - gamma)
    obj = R * R
    obj -= kappa * gamma
    obj += nu_U * sum_U
    obj += nu_L * sum_L
    return obj


def distance_to_center(x_i, center):
    return np.linalg.norm(x_i - center)


def square_distance_to_center(x_i, center):
    return np.dot(x_i - center, x_i - center)


def partial_derivatives_r(x_i, x):
    R, _, c = get_values(x)
    return 2 * R * l_prime(R * R - square_distance_to_center(x_i, c))


def partial_derivatives_c(x_i, x):
    R, _, c = get_values(x)
    return 2 * (x_i - c) * l_prime(R * R - square_distance_to_center(x_i, c))


def partial_derivatives_r_star(x_i, y_i, x):
    R, gamma, c = get_values(x)
    square_dist = square_distance_to_center(x_i, c)
    return 2 * y_i * R * l_prime(y_i * (R * R - square_dist) - gamma)


def partial_derivatives_gamma_star(x_i, y_i, x):
    R, gamma, c = get_values(x)
    return -l_prime(y_i * (R * R - square_distance_to_center(x_i, c)) - gamma)


def partial_derivatives_c_star(x_i, y_i, x):
    R, gamma, c = get_values(x)
    square_dist = square_distance_to_center(x_i, c)
    return 2 * y_i * (x_i - c) * l_prime(y_i * (R * R - square_dist) - gamma)


def gradient_r(x, unlabeled_features, labeled_features, labels, nu_U, nu_L):
    R, _, _ = get_values(x)

    # Unlabeled sum
    num_unlabeled_instances = unlabeled_features.shape[0]
    sum_U = 0
    for i in range(num_unlabeled_instances):
        sum_U += partial_derivatives_r(unlabeled_features[i, :], x)

    # Labeled sum
    sum_L = 0
    num_labeled_instances = labeled_features.shape[0]
    if num_labeled_instances > 0:
        for i in range(num_labeled_instances):
            sum_L += partial_derivatives_r_star(
                labeled_features[i, :], labels[i], x)

    return 2 * R + nu_U * sum_U + nu_L * sum_L


def gradient_gamma(x, labeled_features, labels, kappa, nu_L):
    # Labeled sum
    sum_L = 0
    num_labeled_instances = labeled_features.shape[0]
    if num_labeled_instances > 0:
        for i in range(num_labeled_instances):
            sum_L += partial_derivatives_gamma_star(
                labeled_features[i, :], labels[i], x)

    return -kappa + nu_L * sum_L


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
            sum_L += partial_derivatives_c_star(
                labeled_features[i, :], labels[i], x)

    res = nu_U * sum_U + nu_L * sum_L
    return res


def gradient(x, unlabeled_features, labeled_features, labels, kappa, nu_U,
             nu_L):
    g_r = gradient_r(x, unlabeled_features,
                     labeled_features, labels, nu_U, nu_L)
    g_gamma = gradient_gamma(x, labeled_features, labels, kappa, nu_L)
    return np.concatenate((np.array([g_r, g_gamma]),
                          gradient_c(x, unlabeled_features, labeled_features,
                                     labels, nu_U, nu_L)))


# the features have been scaled before
# compute the center and the radius of the benign and unlabeled instances
# gamma is set to 1
def gen_x_init(unlabeled_features, labeled_features, labels):
    gamma_init = 1.
    c_init, r_init = benign_instances_center_radius(unlabeled_features,
                                                    labeled_features, labels)
    return np.array([r_init, gamma_init] + list(c_init))


def benign_instances_center_radius(unlabeled_features, labeled_features,
                                   labels):
    benign_features = labeled_features[~np.array(labels)]
    if unlabeled_features.shape[0] > 0:
        benign_features = np.concatenate((benign_features, unlabeled_features))
    center = np.mean(benign_features, axis=0)
    radius = np.mean(np.apply_along_axis(
        distance_to_center, 1, benign_features, center))
    return center, radius


def _l(t):
    delta = 0.
    eps = 0.5
    if t <= delta - eps:
        return delta - t
    elif delta - eps <= t and t <= delta + eps:
        return pow(delta + eps - t, 2) / (4. * eps)
    else:
        return 0


def l_prime(t):
    delta = 0.
    eps = 0.5
    if t <= delta - eps:
        return -1.
    elif delta - eps <= t and t <= delta + eps:
        return -0.5 * ((delta - t) / eps + 1.)
    else:
        return 0


def get_values(x):
    R = x[0]
    gamma = x[1]
    c = x[2:]
    return R, gamma, c
