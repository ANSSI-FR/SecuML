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

from secuml.core.classif.monitoring.prediction import PredictionsMonitoring \
        as PredictionsMonitoringCore

from secuml.exp.tools.db_tables import PredictionsAlchemy


class PredictionsMonitoring(PredictionsMonitoringCore):

    def __init__(self, exp):
        PredictionsMonitoringCore.__init__(self, exp.exp_conf.logger)
        self.exp = exp

    def add_fold(self, predictions):
        def to_float(x):
            if x is None:
                return None
            return float(x)
        PredictionsMonitoringCore.add_fold(self, predictions)
        predictions_db = [PredictionsAlchemy(exp_id=self.exp.exp_id,
                                             instance_id=p.instance_id,
                                             value=p.value_to_str(),
                                             proba=to_float(p.proba),
                                             score=to_float(p.score))
                          for p in predictions.to_list()]
        self.exp.session.bulk_save_objects(predictions_db)
