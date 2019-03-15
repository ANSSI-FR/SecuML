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

import abc
import time

from sklearn.externals import joblib
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from secuml.core.data.predictions import Predictions
from secuml.core.tools.core_exceptions import SecuMLcoreException


class SupervisedLearningAtLeastTwoClasses(SecuMLcoreException):

    def __str__(self):
        return('Supervised learning models requires that the training dataset '
               'contains at least two classes.')


class NoCvMonitoring(SecuMLcoreException):

    def __init__(self, model_class):
        self.model_class = model_class.__class__.__name__

    def __str__(self):
        return('%s does not support CV monitoring.' % self.model_class)


class Classifier(object):

    # conf: ClassifierConf
    def __init__(self, conf):
        self.conf = conf
        self._create_pipeline()

    def _create_pipeline(self):
        self.pipeline = Pipeline(self._get_pipeline())

    @abc.abstractmethod
    def _get_pipeline(self):
        return

    @abc.abstractmethod
    def _set_best_hyperparam(self, train_instances):
        return

    def get_supervision(self, instances, ground_truth=False, check=True):
        annotations = instances.get_annotations(ground_truth)
        return annotations.get_supervision(self.conf.multiclass)

    def training(self, instances):
        execution_time = 0
        start = time.time()
        self._set_best_hyperparam(instances)
        execution_time += time.time() - start
        start = time.time()
        self._fit(instances)
        execution_time += time.time() - start
        predictions = self._get_predictions(instances)
        return predictions, execution_time

    def _get_predictions(self, instances):
        predictions = self.apply_pipeline(instances)
        if instances.has_ground_truth():
            ground_truth = self.get_supervision(instances, ground_truth=True,
                                                check=False)
            predictions.set_ground_truth(ground_truth)
        return predictions

    @abc.abstractmethod
    def _fit(self, train_instances):
        return

    def cv_monitoring(self, train_instances, cv_monitoring):
        from secuml.core.classif.conf.test.cv import CvConf
        num_folds = cv_monitoring.num_folds
        cv_test_conf = CvConf(self.conf.logger, None, num_folds)
        cv_datasets = cv_test_conf.gen_datasets(self.conf, train_instances)
        cv_monitoring.init(cv_datasets.get_features_ids())
        for fold_id, datasets in enumerate(cv_datasets._datasets):
            self.pipeline.fit(datasets.train_instances.features.get_values(),
                              self.get_supervision(datasets.train_instances))
            cv_predictions = self._get_predictions(datasets.test_instances)
            cv_monitoring.add_fold(fold_id, cv_predictions, self.pipeline)

    def apply_pipeline(self, instances):
        num_instances = instances.num_instances()
        if num_instances == 0:
            return Predictions([], [], [], [], instances.ids)
        features = instances.features.get_values()
        predictions = self._predict(features)
        all_probas, probas = self._get_predicted_probas(features,
                                                        num_instances)
        scores = self._get_predicted_scores(features, num_instances)
        return Predictions(list(predictions), all_probas, probas, scores,
                           instances.ids)

    def _predict(self, features):
        return self.pipeline.predict(features)

    def _get_predicted_probas(self, features, num_instances):
        if self.conf.probabilist:
            all_predicted_proba = self.pipeline.predict_proba(features)
            if self.conf.multiclass:
                predicted_proba = [None for i in range(num_instances)]
            else:
                predicted_proba = all_predicted_proba[:, 1]
        else:
            all_predicted_proba = [None for i in range(num_instances)]
            predicted_proba = [None for i in range(num_instances)]
        return all_predicted_proba, predicted_proba

    def _get_predicted_scores(self, features, num_instances):
        scoring_func = self.conf.scoring_function()
        if scoring_func is not None:
            return getattr(self.pipeline, scoring_func)(features)
        else:
            return [None for i in range(num_instances)]

    def testing(self, instances):
        start = time.time()
        predictions = self._get_predictions(instances)
        exec_time = time.time() - start
        return predictions, exec_time

    def load_model(self, model_filename):
        self.pipeline = joblib.load(model_filename)


class SupervisedClassifier(Classifier):

    def get_supervision(self, instances, ground_truth=False, check=True):
        supervision = Classifier.get_supervision(self, instances,
                                                 ground_truth=ground_truth,
                                                 check=check)
        if check:
            if len(set(supervision)) < 2:
                raise SupervisedLearningAtLeastTwoClasses
        return supervision

    def _set_best_hyperparam(self, train_instances):
        hyperparam_conf = self.conf.hyperparam_conf
        optim_conf = hyperparam_conf.optim_conf
        cv = StratifiedKFold(n_splits=optim_conf.num_folds)
        param_grid = hyperparam_conf.get_param_grid()
        if param_grid is None:  # No hyper-parameter value to optimize
            return
        grid_search = GridSearchCV(self.pipeline, param_grid=param_grid,
                                   scoring=optim_conf.get_scoring_method(),
                                   cv=cv, iid=False, n_jobs=optim_conf.n_jobs)
        grid_search.fit(train_instances.features.get_values(),
                        self.get_supervision(train_instances))
        hyperparam_conf.values.set_best_values(grid_search)
        best_values = hyperparam_conf.values.get_best_values()
        best_values = {p: value for p, value in best_values.items()}
        self.pipeline.set_params(**best_values)

    def _fit(self, train_instances):
        self.pipeline.fit(train_instances.features.get_values(),
                          self.get_supervision(train_instances))

    def training(self, train_instances):
        predictions, exec_time = Classifier.training(self, train_instances)
        if self.conf.multiclass:
            self.class_labels = self.pipeline.named_steps['model'].classes_
        return predictions, exec_time


class UnsupervisedClassifier(Classifier):

    def _set_best_hyperparam(self, train_instances):
        hyperparam_conf = self.conf.hyperparam_conf
        best_values = hyperparam_conf.values.get_best_values()
        self.pipeline.set_params(**best_values)

    def get_supervision(self, instances, ground_truth=False, check=True):
        if not ground_truth:
            return None
        return Classifier.get_supervision(self, instances,
                                          ground_truth=ground_truth,
                                          check=check)

    # sklearn unsupervised learning algorithms return
    #   -1 for outliers
    #   1 for inliers
    def _predict(self, features):
        predictions = self.pipeline.predict(features)
        return [p == -1 for p in predictions]

    def _fit(self, train_instances):
        self.pipeline.fit(train_instances.features.get_values())


class SemiSupervisedClassifier(Classifier):

    def _set_best_hyperparam(self, train_instances):
        hyperparam_conf = self.conf.hyperparam_conf
        best_values = hyperparam_conf.values.get_best_values()
        self.pipeline.set_params(**best_values)

    # -1 for unlabeled instances.
    def get_supervision(self, instances, ground_truth=False, check=True):
        supervision = Classifier.get_supervision(self, instances,
                                                 ground_truth=ground_truth,
                                                 check=check)
        return [s if s is not None else -1 for s in supervision]

    def _fit(self, train_instances):
        self.pipeline.fit(train_instances.features.get_values(),
                          self.get_supervision(train_instances))
