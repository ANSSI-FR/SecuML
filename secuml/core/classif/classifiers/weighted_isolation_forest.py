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

import numbers
import numpy as np
from scipy.sparse import hstack as sparse_hstack
from scipy.sparse import issparse
from sklearn.tree._tree import DTYPE
from sklearn.utils import check_array
from sklearn.utils import check_random_state
from sklearn.utils._joblib import Parallel, delayed
from sklearn.utils.fixes import parallel_helper, _joblib_parallel_args
from warnings import warn

from .isolation_forest import _IsolationForest
from . import SemiSupervisedClassifier

INTEGER_TYPES = (numbers.Integral, np.integer)


# Implementation of the algorithm presented in the following paper:
# Feedback-Guided Anomaly Discovery via Online Optimization
# Authors: Md Amran Siddiqui, Alan Fern, Thomas D. Dietterich,
#          Ryan Wright, Alec Theriault, David W. Archer
# Presented at KDD 2018.

class _WeightedIsolationForest(_IsolationForest):

    def __init__(self, eta=1.0, n_estimators=100, max_samples='auto',
                 max_features=1.0, n_jobs=None):
        _IsolationForest.__init__(self, n_estimators=n_estimators,
                                  max_samples=max_samples,
                                  contamination='auto', behaviour='new',
                                  max_features=max_features, n_jobs=n_jobs)
        self.eta = eta

    def fit(self, X, y):
        self._fit(X, y)
        self._init_node_weights()
        self.update_node_weights(X, y)
        return self

    def _set_offset(self, X):
        if self.behaviour == 'old':
            # in this case, decision_function = 0.5 + self.score_samples(X):
            if self._contamination == "auto":
                raise ValueError("contamination parameter cannot be set to "
                                 "'auto' when behaviour == 'old'.")

            self.offset_ = -0.5
            self._threshold_ = np.percentile(self.decision_function(X),
                                             100. * self._contamination)
            return

        # else, self.behaviour == 'new':
        if self._contamination == "auto":
            # 0.5 plays a special role as described in the original paper.
            # we take the opposite as we consider the opposite of their score.
            self.offset_ = -0.5
            return

        # else, define offset_ wrt contamination parameter, so that the
        # threshold_ attribute is implicitly 0 and is not needed anymore:
        self.offset_ = np.percentile(self.score_samples(X),
                                     100. * self._contamination)

    def _fit(self, X, y, sample_weight=None):
        if self.contamination == "legacy":
            warn('default contamination parameter 0.1 will change '
                 'in version 0.22 to "auto". This will change the '
                 'predict method behavior.',
                 FutureWarning)
            self._contamination = 0.1
        else:
            self._contamination = self.contamination

        X = check_array(X, accept_sparse=['csc'])
        if issparse(X):
            # Pre-sort indices to avoid that each individual tree of the
            # ensemble sorts the indices.
            X.sort_indices()

        rnd = check_random_state(self.random_state)
        y = rnd.uniform(size=X.shape[0])

        # ensure that max_sample is in [1, n_samples]:
        n_samples = X.shape[0]

        if isinstance(self.max_samples, str):
            if self.max_samples == 'auto':
                max_samples = min(256, n_samples)
            else:
                raise ValueError('max_samples (%s) is not supported.'
                                 'Valid choices are: "auto", int or'
                                 'float' % self.max_samples)

        elif isinstance(self.max_samples, INTEGER_TYPES):
            if self.max_samples > n_samples:
                warn("max_samples (%s) is greater than the "
                     "total number of samples (%s). max_samples "
                     "will be set to n_samples for estimation."
                     % (self.max_samples, n_samples))
                max_samples = n_samples
            else:
                max_samples = self.max_samples
        else:  # float
            if not (0. < self.max_samples <= 1.):
                raise ValueError("max_samples must be in (0, 1], got %r"
                                 % self.max_samples)
            max_samples = int(self.max_samples * X.shape[0])

        self.max_samples_ = max_samples
        max_depth = int(np.ceil(np.log2(max(max_samples, 2))))
        super()._fit(X, y, max_samples,
                     max_depth=max_depth,
                     sample_weight=sample_weight)

    def update_node_weights(self, X, y):
        annotated_mask = y != -1
        num_annotations = np.sum(annotated_mask)
        if num_annotations > 0:
            paths = self.decision_path(X[annotated_mask, :])[0]
            annotations = y[annotated_mask]
            coeffs = np.full((num_annotations, 1), self.eta)
            coeffs[annotations] *= -1
            self.node_weights = np.sum(np.multiply(paths.todense(), coeffs),
                                       axis=0)
            # Set negative weights to zero
            self.node_weights = np.maximum(0, self.node_weights)
            self.node_weights = np.array(self.node_weights).ravel()
        self._set_offset(X)

    def decision_path(self, X):
        return _decision_path(self, X, self.n_jobs)

    def decision_function(self, X):
        return -_IsolationForest.decision_function(self, X)

    def predict(self, X):
        return [p == -1 for p in _IsolationForest.predict(self, X)]

    def _init_node_weights(self):
        num_nodes = sum([estimator.tree_.node_count
                         for estimator in self.estimators_])
        self.node_weights = np.ones(num_nodes, dtype=float)

    def _compute_score_samples(self, X, subsample_features):
        """Compute the score of each samples in X going through the extra trees.

        Parameters
        ----------
        X : array-like or sparse matrix

        subsample_features : bool,
            whether features should be subsampled
        """

        n_samples = X.shape[0]
        depths = np.zeros(n_samples, order='f')
        i = 0

        for tree, features in zip(self.estimators_, self.estimators_features_):
            X_subset = X[:, features] if subsample_features else X
            node_indicator = tree.decision_path(X_subset)
            node_weights = self.node_weights[i:i+node_indicator.shape[1]]
            depths += node_indicator * node_weights
            i += node_indicator.shape[1]

        return -depths


def _decision_path(isolation_forest, X, n_jobs):
    # code from sklearn RandomForest.
    X = check_array(X, dtype=DTYPE, accept_sparse='csr')
    indicators = Parallel(n_jobs=n_jobs,
                          **_joblib_parallel_args(prefer='threads'))(
        delayed(parallel_helper)(tree, 'decision_path', X,
                                 check_input=False)
        for tree in isolation_forest.estimators_)
    n_nodes = [0]
    n_nodes.extend([i.shape[1] for i in indicators])
    n_nodes_ptr = np.array(n_nodes).cumsum()
    indicators = sparse_hstack(indicators).tocsr()
    return indicators, n_nodes_ptr


class WeightedIsolationForest(SemiSupervisedClassifier):

    def _get_pipeline(self):
        return [('model', _WeightedIsolationForest(n_jobs=self.conf.n_jobs))]

    def _update(self, instances):
        self.pipeline['model'].update_node_weights(
                                            instances.features.get_values(),
                                            self._get_supervision(instances))

    # sklearn unsupervised learning algorithms return
    #   -1 for outliers
    #   1 for inliers
    # FIXME a mettre dans la classe _WeightedIsolationForest
    def _predict(self, features, instances_ids):
        predictions = SemiSupervisedClassifier._predict(self, features,
                                                        instances_ids)
        predictions.values = [p == -1 for p in predictions.values]
        return predictions
