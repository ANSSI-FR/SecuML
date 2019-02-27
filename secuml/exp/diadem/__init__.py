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

import os.path as path
from sqlalchemy.orm.exc import NoResultFound

from secuml.exp import experiment
from secuml.exp.conf.annotations import AnnotationsConf
from secuml.exp.conf.dataset import DatasetConf
from secuml.exp.tools.db_tables import DiademExpAlchemy
from secuml.exp.tools.db_tables import ExpAlchemy
from secuml.exp.tools.db_tables import ExpRelationshipsAlchemy
from secuml.exp.experiment import Experiment
from secuml.exp.tools.exp_exceptions import SecuMLexpException

from .conf.diadem import DiademConf
from .conf.train_test import TestConf
from .conf.train_test import TrainConf
from .monitoring.train_test import CvMonitoring
from .train_test import TestExp
from .train_test import TrainExp


class NoGroundTruth(SecuMLexpException):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ExperimentNotFound(SecuMLexpException):

    def __init__(self, exp_id):
        self.exp_id = exp_id

    def __str__(self):
        return('The experiment %d cannot be found.' % (self.exp_id))


class InvalidModelExperimentKind(SecuMLexpException):

    def __init__(self, exp_kind):
        self.exp_kind = exp_kind

    def __str__(self):
        return('model-exp-id is a %s experiment '
               'while it must be a DIADEM or an ActiveLearning experiment.'
               % (self.exp_kind))


def add_diadem_exp_to_db(session, exp_id, fold_id, kind, alerts_conf=None,
                         classifier_conf=None):
    if classifier_conf is not None:
        multiclass = classifier_conf.multiclass
        proba = classifier_conf.is_probabilist()
        with_scoring = classifier_conf.scoring_function() is not None
        if kind in ['train', 'cv']:
            perf_monitoring = True
            alerts = False
        elif kind in ['test', 'validation', 'alerts']:
            perf_monitoring = False
            alerts = alerts_conf is not None
        model_interp = classifier_conf.is_interpretable()
        if kind == 'cv':
            predictions_interp = False
        else:
            predictions_interp = classifier_conf.interpretable_predictions()
        exp = DiademExpAlchemy(exp_id=exp_id, fold_id=fold_id, type=kind,
                               perf_monitoring=perf_monitoring, alerts=alerts,
                               model_interpretation=model_interp,
                               predictions_interpretation=predictions_interp,
                               multiclass=multiclass, proba=proba,
                               with_scoring=with_scoring)
    else:
        exp = DiademExpAlchemy(exp_id=exp_id, fold_id=fold_id, type=kind)
    session.add(exp)
    session.flush()


def _get_exp_row(session, exp_id):
    query = session.query(ExpAlchemy)
    query = query.filter(ExpAlchemy.id == exp_id)
    try:
        return query.one()
    except NoResultFound:
        return None


class DiademExp(Experiment):

    def __init__(self, exp_conf, create=True, session=None):
        Experiment.__init__(self, exp_conf, create, session)
        self.test_conf = self.exp_conf.core_conf.test_conf
        self.validation_conf = self.exp_conf.core_conf.validation_conf
        self._train_test_exps = {}

    def run(self, instances=None, cv_monitoring=False):
        Experiment.run(self)
        datasets = self._gen_datasets(instances)
        if self.test_conf.method in ['cv', 'temporal_cv', 'sliding_window']:
            self._run_cv(datasets, cv_monitoring)
        else:
            self._run_one_fold(datasets, cv_monitoring)

    def web_template(self):
        return 'diadem/main.html'

    def get_train_test_exp(self, train_test, fold_id=None):
        if fold_id is not None:
            return self._train_test_exps['folds'][fold_id][train_test]
        else:
            return self._train_test_exps[train_test]

    def get_predictions(self, train_test, fold_id):
        return self.get_train_test_exp(train_test, fold_id).predictions

    def _create_train_exp(self, fold_id=None):
        diadem_id = self.exp_conf.exp_id
        exp_name = 'DIADEM_%i_Train' % diadem_id
        if fold_id is not None:
            exp_name = '%s_fold_%i' % (exp_name, fold_id)
        train_exp_conf = TrainConf(self.exp_conf.secuml_conf,
                                   self.exp_conf.dataset_conf,
                                   self.exp_conf.features_conf,
                                   self.exp_conf.annotations_conf,
                                   self.exp_conf.core_conf.classifier_conf,
                                   name=exp_name, parent=diadem_id,
                                   fold_id=fold_id)
        return TrainExp(train_exp_conf, session=self.session)

    def _set_train_exp_id(self):
        train_exp_id = self._check_already_trained_conf()
        exp_relation = ExpRelationshipsAlchemy(child_id=train_exp_id,
                                               parent_id=self.exp_conf.exp_id)
        self.session.add(exp_relation)
        return train_exp_id

    def _get_trained_classifier(self, train_exp_id):
        trained_exp = experiment.get_factory().from_exp_id(
                                                      train_exp_id,
                                                      self.exp_conf.secuml_conf,
                                                      self.session)
        trained_conf = trained_exp.exp_conf.core_conf
        trained_classifier = trained_conf.model_class(trained_conf)
        trained_classifier.load_model(path.join(trained_exp.output_dir(),
                                                'model.out'))
        return trained_classifier

    def _check_already_trained_conf(self):
        already_trained_id = self.exp_conf.already_trained
        model_exp = _get_exp_row(self.session, already_trained_id)
        # Check whether the experiment exists
        if model_exp is None:
            raise ExperimentNotFound(already_trained_id)
        # Check the type of the experiment
        if model_exp.kind == 'Diadem':
            query = self.session.query(DiademExpAlchemy)
            query = query.join(DiademExpAlchemy.exp)
            query = query.join(ExpAlchemy.parents)
            query = query.filter(ExpRelationshipsAlchemy.parent_id == already_trained_id)
            query = query.filter(DiademExpAlchemy.type == 'train')
            query = query.filter(DiademExpAlchemy.fold_id == None)
            res = query.one()
            return res.exp_id
        elif model_exp.kind == 'ActiveLearning':
            return None
        else:
            raise InvalidModelExperimentKind(model_exp.kind)

    def _create_test_exp(self, classifier, fold_id=None):
        diadem_id = self.exp_conf.exp_id
        exp_name = 'DIADEM_%i_Test' % diadem_id
        if fold_id is not None:
            exp_name = '%s_fold_%i' % (exp_name, fold_id)
        secuml_conf = self.exp_conf.secuml_conf
        logger = secuml_conf.logger
        if self.test_conf.method == 'dataset':
            dataset_conf = DatasetConf(self.exp_conf.dataset_conf.project,
                                       self.test_conf.test_dataset,
                                       self.exp_conf.secuml_conf.logger)
            annotations_conf = AnnotationsConf('ground_truth.csv', None, logger)
        else:
            dataset_conf = self.exp_conf.dataset_conf
            annotations_conf = self.exp_conf.annotations_conf
        features_conf = self.exp_conf.features_conf
        test_exp_conf = TestConf(secuml_conf, dataset_conf, features_conf,
                                 annotations_conf,
                                 self.exp_conf.core_conf.classifier_conf,
                                 name=exp_name, parent=diadem_id,
                                 fold_id=fold_id, kind='test')
        return TestExp(test_exp_conf, classifier=classifier,
                       alerts_conf=self._get_alerts_conf(fold_id),
                       session=self.session)

    def _create_validation_exp(self, classifier, fold_id=None):
        assert(self.validation_conf.method == 'dataset')
        diadem_id = self.exp_conf.exp_id
        exp_name = 'DIADEM_%i_Validation' % diadem_id
        if fold_id is not None:
            exp_name = '%s_fold_%i' % (exp_name, fold_id)
        secuml_conf = self.exp_conf.secuml_conf
        logger = secuml_conf.logger
        dataset_conf = DatasetConf(self.exp_conf.dataset_conf.project,
                                   self.validation_conf.test_dataset,
                                   self.exp_conf.secuml_conf.logger)
        annotations_conf = AnnotationsConf('ground_truth.csv', None, logger)
        features_conf = self.exp_conf.features_conf
        test_exp_conf = TestConf(secuml_conf, dataset_conf, features_conf,
                                 annotations_conf,
                                 self.exp_conf.core_conf.classifier_conf,
                                 name=exp_name, parent=diadem_id,
                                 kind='validation')
        return TestExp(test_exp_conf, classifier=classifier,
                       alerts_conf=self._get_alerts_conf(fold_id),
                       session=self.session)

    def _get_alerts_conf(self, fold_id):
        if fold_id is not None:
            return None
        return self.exp_conf.core_conf.test_conf.alerts_conf

    def _run_one_fold(self, datasets, cv_monitoring, fold_id=None):
        classifier = self._train(datasets, cv_monitoring, fold_id)
        test_predictions = self._test(classifier, datasets, fold_id)
        if self.validation_conf:
            self._validate(classifier, datasets, fold_id)
        return classifier, test_predictions

    def _train(self, datasets, cv_monitoring, fold_id):
        if self.exp_conf.already_trained is not None:
            train_exp_id = self._set_train_exp_id()
            self._set_train_test_exp('train', None, fold_id)
            return self._get_trained_classifier(train_exp_id)
        else:
            train_exp = self._create_train_exp(fold_id=fold_id)
            train_exp.run(datasets.train_instances, cv_monitoring)
            self._set_train_test_exp('train', train_exp, fold_id)
            return train_exp.classifier

    def _test(self, classifier, datasets, fold_id):
        test_exp = self._create_test_exp(classifier, fold_id=fold_id)
        test_exp.run(datasets.test_instances)
        self._set_train_test_exp('test', test_exp, fold_id)
        return test_exp.predictions

    def _validate(self, classifier, datasets, fold_id):
        validation_exp = self._create_validation_exp(classifier,
                                                     fold_id=fold_id)
        validation_exp.run(None)
        self._set_train_test_exp('validation', validation_exp, fold_id)

    def _run_cv(self, cv_datasets, cv_monitoring):
        classifiers = [None for _ in range(self.test_conf.num_folds)]
        classifier_conf = self.exp_conf.core_conf.classifier_conf
        add_diadem_exp_to_db(self.session, self.exp_conf.exp_id, None, 'cv',
                             classifier_conf=classifier_conf)
        global_cv_monitoring = CvMonitoring(
                                        self, self.test_conf.num_folds,
                                        self.exp_conf.core_conf.classifier_conf)
        global_cv_monitoring.init(cv_datasets.get_features_ids())
        for fold_id, datasets in enumerate(cv_datasets._datasets):
            classifier, test_predictions = self._run_one_fold(datasets,
                                                              cv_monitoring,
                                                              fold_id)
            global_cv_monitoring.add_fold(fold_id, test_predictions,
                                          classifier.pipeline)
            classifiers[fold_id] = classifier
        global_cv_monitoring.display(self.output_dir())
        return classifiers

    def _gen_datasets(self, instances):
        if instances is None:
            instances = self.get_instances()
        classifier_conf = self.exp_conf.core_conf.classifier_conf
        return self.test_conf.gen_datasets(classifier_conf, instances)

    def _set_train_test_exp(self, train_test, exp, fold_id):
        if fold_id is None:
            self._train_test_exps[train_test] = exp
        else:
            if 'folds' not in self._train_test_exps:
                self._train_test_exps['folds'] = {}
            if fold_id not in self._train_test_exps['folds']:
                self._train_test_exps['folds'][fold_id] = {}
            self._train_test_exps['folds'][fold_id][train_test] = exp


experiment.get_factory().register('Diadem', DiademExp, DiademConf)
