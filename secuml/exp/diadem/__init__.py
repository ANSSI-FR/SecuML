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

import os.path as path
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import null

from secuml.exp import experiment
from secuml.exp.conf.annotations import AnnotationsConf
from secuml.exp.conf.dataset import DatasetConf
from secuml.exp.tools.db_tables import DiademExpAlchemy
from secuml.exp.tools.db_tables import ExpAlchemy
from secuml.exp.tools.db_tables import ExpRelationshipsAlchemy
from secuml.exp.experiment import Experiment
from secuml.exp.tools.exp_exceptions import SecuMLexpException

from .conf.diadem import DiademConf
from .conf.detection import DetectionConf
from .conf.train import TrainConf
from .detection import DetectionExp
from .monitoring import CvMonitoring
from .train import TrainExp


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


def add_diadem_exp_to_db(session, exp_id, dataset_id, fold_id, kind,
                         classifier_conf=None):
    if classifier_conf is not None:
        multiclass = classifier_conf.multiclass
        proba = classifier_conf.is_probabilist()
        with_scoring = classifier_conf.scoring_function() is not None
        if kind in ['train', 'cv']:
            perf_monitoring = True
        elif kind in ['test', 'validation', 'alerts']:
            perf_monitoring = False
        model_interp = classifier_conf.is_interpretable()
        if kind == 'cv':
            predictions_interp = False
        else:
            predictions_interp = classifier_conf.interpretable_predictions()
        exp = DiademExpAlchemy(exp_id=exp_id, fold_id=fold_id, type=kind,
                               perf_monitoring=perf_monitoring,
                               model_interp=model_interp,
                               pred_interp=predictions_interp,
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
        self._init_children_exps()

    def run(self, instances=None, cv_monitoring=False):
        Experiment.run(self)
        datasets = self._gen_datasets(instances)
        if self.test_conf.method in ['cv', 'temporal_cv', 'sliding_window']:
            self._run_cv(datasets, cv_monitoring)
        else:
            self._run_one_fold(datasets, cv_monitoring)

    def web_template(self):
        return 'diadem/main.html'

    def get_train_exp(self):
        return self._train_exp

    def get_detection_exp(self, kind):
        return self._detection_exp[kind]

    def get_predictions(self, kind):
        return self.get_detection_exp(kind).predictions

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
            query = query.filter(
                       ExpRelationshipsAlchemy.parent_id == already_trained_id)
            query = query.filter(DiademExpAlchemy.type == 'train')
            query = query.filter(DiademExpAlchemy.fold_id == null())
            res = query.one()
            return res.exp_id
        elif model_exp.kind == 'ActiveLearning':
            return None
        else:
            raise InvalidModelExperimentKind(model_exp.kind)

    # kind in ['train', 'test', 'validation']
    def _create_detection_exp(self, kind, classifier_conf, fold_id=None):
        diadem_id = self.exp_conf.exp_id
        exp_name = 'DIADEM_%i_Detection_%s' % (diadem_id, kind)
        if fold_id is not None:
            exp_name = '%s_fold_%i' % (exp_name, fold_id)
        secuml_conf = self.exp_conf.secuml_conf
        logger = secuml_conf.logger
        if (kind == 'validation' or
                (kind == 'test' and self.test_conf.method == 'dataset')):
            validation_conf = getattr(self, '%s_conf' % kind)
            dataset_conf = DatasetConf(self.exp_conf.dataset_conf.project,
                                       validation_conf.test_dataset,
                                       self.exp_conf.secuml_conf.logger)
            annotations_conf = AnnotationsConf('ground_truth.csv', None,
                                               logger)
            features_conf = self.exp_conf.features_conf
            if validation_conf.streaming:
                stream_batch = validation_conf.stream_batch
                features_conf = features_conf.copy_streaming(stream_batch)
        else:
            dataset_conf = self.exp_conf.dataset_conf
            annotations_conf = self.exp_conf.annotations_conf
            features_conf = self.exp_conf.features_conf
        alerts_conf = None
        if fold_id is None and kind != 'train':
            alerts_conf = self.exp_conf.alerts_conf
        test_exp_conf = DetectionConf(
                            secuml_conf, dataset_conf, features_conf,
                            annotations_conf, alerts_conf, name=exp_name,
                            parent=diadem_id, fold_id=fold_id, kind=kind)
        return DetectionExp(test_exp_conf, session=self.session)

    def _run_one_fold(self, datasets, cv_monitoring, fold_id=None):
        classifier, train_time = self._train(datasets, cv_monitoring, fold_id)
        self._detection('train', classifier, datasets.train_instances,
                        fold_id)
        test_predictions, test_time = self._detection('test', classifier,
                                                      datasets.test_instances,
                                                      fold_id)
        if self.validation_conf:
            self._detection('validation', classifier, None, fold_id)
        return classifier, train_time, test_predictions, test_time

    def _train(self, datasets, cv_monitoring, fold_id):
        if self.exp_conf.already_trained is not None:
            train_exp_id = self._set_train_exp_id()
            return self._get_trained_classifier(train_exp_id), 0
        else:
            train_exp = self._create_train_exp(fold_id=fold_id)
            train_exp.run(datasets.train_instances, cv_monitoring)
            if fold_id is None:
                self._set_train_exp(train_exp)
            return train_exp.classifier, train_exp.train_time

    # kind: train, test, validation
    def _detection(self, kind, classifier, instances, fold_id):
        detection_exp = self._create_detection_exp(kind, classifier.conf,
                                                   fold_id=fold_id)
        if fold_id is None:
            self._set_detection_exp(kind, detection_exp)
        detection_exp.run(instances, classifier)
        return detection_exp.predictions, detection_exp.prediction_time

    def _run_cv(self, cv_datasets, cv_monitoring):
        classifiers = [None for _ in range(self.test_conf.num_folds)]
        classifier_conf = self.exp_conf.core_conf.classifier_conf
        add_diadem_exp_to_db(self.session, self.exp_conf.exp_id, None, 'cv',
                             classifier_conf=classifier_conf)
        global_cv_monitoring = CvMonitoring(self, self.test_conf.num_folds)
        for fold_id, datasets in enumerate(cv_datasets._datasets):
            classifier, train_t, predictions, test_t = self._run_one_fold(
                                                                 datasets,
                                                                 cv_monitoring,
                                                                 fold_id)
            global_cv_monitoring.add_fold(classifier, train_t, predictions,
                                          test_t, fold_id)
            classifiers[fold_id] = classifier
        global_cv_monitoring.display(self.output_dir())
        return classifiers

    def _gen_datasets(self, instances):
        if instances is None:
            instances = self.get_instances()
        classifier_conf = self.exp_conf.core_conf.classifier_conf
        return self.test_conf.gen_datasets(classifier_conf, instances)

    # kind in ['train', 'test', 'validation']
    def _set_detection_exp(self, kind, exp):
        self._detection_exp[kind] = exp

    def _set_train_exp(self, exp):
        self._train_exp = exp

    def _init_children_exps(self):
        self._train_exp = None
        if self.test_conf.method in ['cv', 'temporal_cv', 'sliding_window']:
            self._detection_exp = None
        else:
            self._detection_exp = {}
            for kind in ['train', 'test', 'validation']:
                self._detection_exp[kind] = None


experiment.get_factory().register('Diadem', DiademExp, DiademConf)
