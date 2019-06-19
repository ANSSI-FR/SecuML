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
from secuml.exp.experiment import Experiment

from .conf.train import TrainConf
from .monitoring import CvMonitoring
from .monitoring import TrainMonitoring


class TrainExp(Experiment):

    def __init__(self, exp_conf, create=True, session=None):
        Experiment.__init__(self, exp_conf, create=create, session=session)
        self.classifier = None
        self.train_time = None
        self.monitoring = TrainMonitoring(self)

    def run(self, train_instances, cv_monitoring=False, init_classifier=None):
        Experiment.run(self)
        self._train(train_instances, init_classifier)
        if cv_monitoring:
            self._cv_monitoring(train_instances)
        self.monitoring.display(self.output_dir())

    def add_to_db(self):
        from secuml.exp.diadem import add_diadem_exp_to_db
        Experiment.add_to_db(self)
        add_diadem_exp_to_db(self.session, self.exp_conf.exp_id,
                             self.exp_conf.dataset_conf.dataset_id,
                             self.exp_conf.fold_id, 'train',
                             classifier_conf=self.exp_conf.core_conf)

    def _train(self, train_instances, init_classifier):
        if init_classifier is not None:
            self.classifier = init_classifier
            self.train_time = self.classifier.update(train_instances)
        else:
            classifier_conf = self.exp_conf.core_conf
            self.classifier = classifier_conf.model_class(classifier_conf)
            self.train_time = self.classifier.training(train_instances)
        self.monitoring.set_classifier(self.classifier, self.train_time)

    def _cv_monitoring(self, train_instances):
        classifier_conf = self.exp_conf.core_conf
        num_folds = classifier_conf.hyperparam_conf.optim_conf.num_folds
        cv_monitoring = CvMonitoring(self, num_folds)
        try:
            self.classifier.cv_monitoring(train_instances, cv_monitoring)
            self.monitoring.set_cv_monitoring(cv_monitoring)
        except NoCvMonitoring as e:
            self.logger.warning(str(e))


experiment.get_factory().register('Train', TrainExp, TrainConf)
