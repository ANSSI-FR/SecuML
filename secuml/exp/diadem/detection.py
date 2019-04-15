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

from secuml.exp import experiment
from secuml.exp.tools.db_tables import DiademExpAlchemy
from secuml.exp.experiment import Experiment

from .conf.detection import DetectionConf
from .monitoring import DetectionMonitoring


def diadem_set_perf_monitoring(session, exp_id):
    query = session.query(DiademExpAlchemy)
    query = query.filter(DiademExpAlchemy.exp_id == exp_id)
    row = query.one()
    row.perf_monitoring = True
    session.flush()


class DetectionExp(Experiment):

    def __init__(self, exp_conf, create=True, session=None):
        self.kind = exp_conf.kind
        Experiment.__init__(self, exp_conf, create=create, session=session)
        self.test_instances = None
        self.predictions = None
        self.prediction_time = None
        self.classifier = None
        self.monitoring = DetectionMonitoring(
                                           self,
                                           alerts_conf=self.exp_conf.core_conf)

    def run(self, test_instances, classifier):
        Experiment.run(self)
        self.classifier = classifier
        self.test_instances = self.get_instances(test_instances)
        self._test(classifier)
        self._export()

    def web_template(self):
        return 'diadem/detection.html'

    def add_to_db(self):
        Experiment.add_to_db(self)
        self.session.add(DiademExpAlchemy(exp_id=self.exp_conf.exp_id,
                                          fold_id=self.exp_conf.fold_id,
                                          type=self.kind))
        self.session.flush()

    def _test(self, classifier):
        if self.test_instances.has_ground_truth():
            diadem_set_perf_monitoring(self.session, self.exp_conf.exp_id)
        self.predictions, self.prediction_time = classifier.testing(
                                                           self.test_instances)
        self.monitoring.add_predictions(self.predictions, self.prediction_time)

    def _export(self):
        self.monitoring.display(self.output_dir())
        self._set_diadem_conf()

    def _set_diadem_conf(self):
        classif_conf = self.classifier.conf
        query = self.session.query(DiademExpAlchemy)
        query = query.filter(DiademExpAlchemy.exp_id == self.exp_conf.exp_id)
        diadem_exp = query.one()
        diadem_exp.multiclass = classif_conf.multiclass
        diadem_exp.proba = classif_conf.is_probabilist()
        diadem_exp.with_scoring = classif_conf.scoring_function() is not None
        diadem_exp.alerts = (self.exp_conf.core_conf is not None and
                             not classif_conf.multiclass)
        diadem_exp.model_interp = classif_conf.is_interpretable()
        diadem_exp.pred_interp = classif_conf.interpretable_predictions()
        self.session.flush()


experiment.get_factory().register('Detection', DetectionExp, DetectionConf)
