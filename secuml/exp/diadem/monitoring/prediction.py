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

import numpy as np

from secuml.core.classif.monitoring.prediction import PredictionsMonitoring \
        as PredictionsMonitoringCore

from secuml.exp.tools.db_tables import PredictionsAlchemy


class PredictionsMonitoring(PredictionsMonitoringCore):

    def __init__(self, exp):
        PredictionsMonitoringCore.__init__(self, exp.exp_conf.logger)
        self.exp = exp

    def final_computations(self):
        def to_float(x):
            return None if x is None else float(x)
        def to_int(x):
            return None if x is None else int(x)
        PredictionsMonitoringCore.final_computations(self)
        predictions_db = [PredictionsAlchemy(exp_id=self.exp.exp_id,
                                             instance_id=p.instance_id,
                                             value=p.value_to_str(),
                                             proba=to_float(p.proba),
                                             score=to_float(p.score),
                                             rank=to_int(p.rank))
                          for p in self.predictions.to_list()]
        self.exp.session.bulk_save_objects(predictions_db)
