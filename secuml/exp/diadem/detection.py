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


class DetectionExp(Experiment):

    def __init__(self, exp_conf, create=True, session=None):
        self.kind = exp_conf.kind
        Experiment.__init__(self, exp_conf, create=create, session=session)
        self.test_instances = None
        self.predictions = None
        self.prediction_time = None
        self.classifier = None
        alerts_conf = self.exp_conf.core_conf
        self.monitoring = DetectionMonitoring(self, alerts_conf=alerts_conf)

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
        has_ground_truth = self.exp_conf.dataset_conf.has_ground_truth
        self.session.add(DiademExpAlchemy(exp_id=self.exp_conf.exp_id,
                                          fold_id=self.exp_conf.fold_id,
                                          type=self.kind,
                                          perf_monitoring=has_ground_truth))
        self.session.flush()

    def _test(self, classifier):
        self.predictions, self.prediction_time = classifier.testing(
                                                           self.test_instances)
        self.monitoring.add_predictions(self.predictions, self.prediction_time)

    def _export(self):
        self.monitoring.display(self.output_dir())
        self._set_diadem_conf()

    def _set_diadem_conf(self):
        info = self.predictions.info
        query = self.session.query(DiademExpAlchemy)
        query = query.filter(DiademExpAlchemy.exp_id == self.exp_conf.exp_id)
        diadem_exp = query.one()
        diadem_exp.multiclass = info.multiclass
        diadem_exp.proba = info.with_probas
        diadem_exp.with_scoring = info.with_scores
        if self.classifier is not None:
            classif_conf = self.classifier.conf
            diadem_exp.model_interp = classif_conf.is_interpretable()
            diadem_exp.pred_interp = classif_conf.interpretable_predictions()

        self.session.flush()


experiment.get_factory().register('Detection', DetectionExp, DetectionConf)
