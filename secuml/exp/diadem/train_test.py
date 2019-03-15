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

from secuml.core.classif.classifiers import NoCvMonitoring
from secuml.exp import experiment
from secuml.exp.tools.db_tables import DiademExpAlchemy
from secuml.exp.experiment import Experiment

from .conf.train_test import TestConf
from .conf.train_test import TrainConf
from .monitoring.train_test import CvMonitoring
from .monitoring.train_test import TestMonitoring
from .monitoring.train_test import TrainMonitoring


def diadem_set_perf_monitoring(session, exp_id):
    query = session.query(DiademExpAlchemy)
    query = query.filter(DiademExpAlchemy.exp_id == exp_id)
    row = query.one()
    row.perf_monitoring = True
    session.flush()


class TrainExp(Experiment):

    def __init__(self, exp_conf, create=True, session=None):
        Experiment.__init__(self, exp_conf, create=create, session=session)
        self.classifier = None
        self.predictions = None
        self.monitoring = None
        self.cv_monitoring = None

    def run(self, train_instances, cv_monitoring=False):
        Experiment.run(self)
        self._train(train_instances)
        if cv_monitoring:
            self._cv_monitoring(train_instances)
        else:
            self.cv_monitoring = None
        self._export()

    def add_to_db(self):
        from secuml.exp.diadem import add_diadem_exp_to_db
        Experiment.add_to_db(self)
        add_diadem_exp_to_db(self.session, self.exp_conf.exp_id,
                             self.exp_conf.fold_id, 'train',
                             classifier_conf=self.exp_conf.core_conf)

    def _train(self, train_instances):
        classifier_conf = self.exp_conf.core_conf
        self.classifier = classifier_conf.model_class(classifier_conf)
        self.predictions, exec_time = self.classifier.training(train_instances)
        self.monitoring = TrainMonitoring(self, exec_time)
        self.monitoring.init(train_instances.get_features_ids())
        self.monitoring.add_fold(0, self.predictions, self.classifier.pipeline)

    def _cv_monitoring(self, train_instances):
        classifier_conf = self.exp_conf.core_conf
        num_folds = classifier_conf.hyperparam_conf.optim_conf.num_folds
        self.cv_monitoring = CvMonitoring(self, num_folds,
                                          self.exp_conf.core_conf)
        try:
            self.classifier.cv_monitoring(train_instances, self.cv_monitoring)
        except NoCvMonitoring as e:
            self.logger.warning(str(e))
            self.cv_monitoring = None

    def _export(self):
        self.monitoring.display(self.output_dir())
        if self.cv_monitoring is not None:
            self.cv_monitoring.display(self.output_dir())


class TestExp(Experiment):

    def __init__(self, exp_conf, classifier=None, alerts_conf=None,
                 create=True, session=None):
        self.classifier = classifier
        self.kind = exp_conf.kind
        self.alerts_conf = alerts_conf
        self.test_instances = None
        self.predictions = None
        self.monitoring = None
        Experiment.__init__(self, exp_conf, create=create, session=session)

    def run(self, test_instances):
        Experiment.run(self)
        self.test_instances = self.get_instances(test_instances)
        self._test()
        self._export()

    def web_template(self):
        return 'diadem/test.html'

    def add_to_db(self):
        Experiment.add_to_db(self)
        from secuml.exp.diadem import add_diadem_exp_to_db
        add_diadem_exp_to_db(self.session, self.exp_conf.exp_id,
                             self.exp_conf.fold_id, self.kind,
                             alerts_conf=self.alerts_conf,
                             classifier_conf=self.classifier.conf)

    def _test(self):
        if self.test_instances.has_ground_truth():
            diadem_set_perf_monitoring(self.session, self.exp_conf.exp_id)
        self.predictions, exec_time = self.classifier.testing(
                                                           self.test_instances)
        self.monitoring = TestMonitoring(self, self.classifier.conf, exec_time,
                                         alerts_conf=self.alerts_conf)
        self.monitoring.init(self.test_instances)
        self.monitoring.add_predictions(self.predictions)

    def _export(self):
        self.monitoring.display(self.output_dir())


experiment.get_factory().register('Train', TrainExp, TrainConf)
experiment.get_factory().register('Test', TestExp, TestConf)
