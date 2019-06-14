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
from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler

from . import SemiSupervisedClassifier


class _Sssvdd(BaseEstimator):

    def __init__(self, nu_l=1., nu_u=1., kappa=1.):
        self.nu_l = nu_l
        self.nu_u = nu_u
        self.kappa = kappa
        self.c = None
        self.r = None

    def fit(self, X, y):
        unlabeled_mask = np.array([annotation == -1 for annotation in y])
        X_unlabeled = X[unlabeled_mask, :]
        X_labeled = X[~unlabeled_mask, :]
        y_labeled = np.array([-1. if annotation else 1. for annotation in y
                              if annotation != -1])
        num_labeled_instances = X_labeled.shape[0]
        num_unlabeled_instances = X_unlabeled.shape[0]

        # To avoid numerical instability
        if num_labeled_instances > 0:
            self.nu_l /= num_labeled_instances
        if num_unlabeled_instances > 0:
            self.nu_u /= num_unlabeled_instances

        x_init = gen_x_init(X_unlabeled, X_labeled, y_labeled)
        # disp=False, not to display the convergence message.
        optim_res = scipy.optimize.fmin_bfgs(objective,
                                             x_init,
                                             fprime=gradient,
                                             args=(X_unlabeled, X_labeled,
                                                   y_labeled, self.kappa,
                                                   self.nu_u, self.nu_l),
                                             disp=False)
        self.r, _, self.c = get_values(optim_res)

    def decision_function(self, X):
        return np.apply_along_axis(predict_score, 1, X, self.c, self.r)

    def predict(self, X):
        return np.apply_along_axis(predict_label, 1, X, self.c, self.r)

    def predict_from_scores(self, X, scores):
        is_outlier = np.full(X.shape[0], False, dtype=int)
        is_outlier[scores > 0] = True
        return is_outlier


class Sssvdd(SemiSupervisedClassifier):

    def _get_pipeline(self):
        return [('scaler', StandardScaler()),
                ('model', _Sssvdd(nu_l=self.conf.nu_l, nu_u=self.conf.nu_u,
                                  kappa=self.conf.kappa))]


def predict_label(x, center, r):
    return predict_score(x, center, r) > 0


def predict_score(x, center, r):
    return square_distance_to_center(x, center) - pow(r, 2)


def objective(x, unlabeled_features, labeled_features, labels, kappa, nu_u,
              nu_l):
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
    obj += nu_u * sum_U
    obj += nu_l * sum_L
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


def gradient_r(x, unlabeled_features, labeled_features, labels, nu_u, nu_l):
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

    return 2 * R + nu_u * sum_U + nu_l * sum_L


def gradient_gamma(x, labeled_features, labels, kappa, nu_l):
    # Labeled sum
    sum_L = 0
    num_labeled_instances = labeled_features.shape[0]
    if num_labeled_instances > 0:
        for i in range(num_labeled_instances):
            sum_L += partial_derivatives_gamma_star(
                labeled_features[i, :], labels[i], x)

    return -kappa + nu_l * sum_L


def gradient_c(x, unlabeled_features, labeled_features, labels, nu_u, nu_l):
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

    res = nu_u * sum_U + nu_l * sum_L
    return res


def gradient(x, unlabeled_features, labeled_features, labels, kappa, nu_u,
             nu_l):
    g_r = gradient_r(x, unlabeled_features,
                     labeled_features, labels, nu_u, nu_l)
    g_gamma = gradient_gamma(x, labeled_features, labels, kappa, nu_l)
    return np.concatenate((np.array([g_r, g_gamma]),
                          gradient_c(x, unlabeled_features, labeled_features,
                                     labels, nu_u, nu_l)))


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
    benign_features = labeled_features[labels == 1, :]
    if unlabeled_features.shape[0] > 0:
        benign_features = np.concatenate((benign_features, unlabeled_features))
    center = np.mean(benign_features, axis=0)
    radius = np.mean(np.apply_along_axis(distance_to_center, 1,
                                         benign_features, center))
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
