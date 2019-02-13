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

from secuml.core.active_learning.update_model import UpdateModel \
        as CoreUpdateModel
from secuml.exp.diadem.conf.diadem import DiademConf
from secuml.exp.diadem import DiademExp

from .monitoring.model_perf import ModelPerfEvolution


class UpdateModel(CoreUpdateModel):

    def __init__(self, iteration):
        CoreUpdateModel.__init__(self, iteration)
        self.exp = self.iteration.exp
        self.model_exp = None

    def execute(self):
        name = 'AL%d-Iter%d-main' % (self.exp.exp_id,
                                     self.iteration.iter_num)
        exp_conf = DiademConf(self.exp.exp_conf.secuml_conf,
                              self.exp.exp_conf.dataset_conf,
                              self.exp.exp_conf.features_conf,
                              self.exp.exp_conf.annotations_conf,
                              self.model_conf, name=name,
                              parent=self.exp.exp_id)
        self.model_exp = DiademExp(exp_conf, session=self.exp.session)
        self.model_exp.run(instances=self.iteration.datasets.instances,
                           cv_monitoring=True)
        self._set_exec_time()
        self.classifier = self.model_exp.get_train_test_exp('train').classifier

    def _set_exec_time(self):
        train_monitoring = self.model_exp.get_train_test_exp('train').monitoring
        test_monitoring = self.model_exp.get_train_test_exp('test').monitoring
        self.exec_time = sum([m.exec_time for m in [train_monitoring,
                                                    test_monitoring]])

    def monitoring(self, al_dir, iteration_dir):
        with_validation = self.iteration.conf.validation_conf is not None
        self.monitoring = ModelPerfEvolution(self.iteration.iter_num,
                                             self.model_exp, with_validation)
        self.monitoring.generate()
        self.monitoring.export(iteration_dir, al_dir)
