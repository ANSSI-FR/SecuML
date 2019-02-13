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

from secuml.core.active_learning.strategies.rcd import Rcd as CoreRcd
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.exp.active_learning.queries.rcd import RcdQueries
from secuml.exp.tools.db_tables import RcdClusteringExpAlchemy


class Rcd(CoreRcd):

    def _set_queries(self):
        self.queries['rcd'] = RcdQueries(self.iteration, 'all')

    def generate_queries(self, predictions):
        rcd_row = RcdClusteringExpAlchemy(id=self.iteration.exp.exp_id,
                                          iter=self.iteration.iter_num,
                                          clustering_exp=None)
        self.iteration.exp.session.add(rcd_row)
        query = self.queries['rcd']
        query.run(predictions)
        clustering_exp = -1
        if query.clustering_exp is not None:
            rcd_row.clustering_exp = query.clustering_exp.exp_id
        else:
            rcd_row.clustering_exp = -1
        self.iteration.exp.session.commit()
        self.exec_time = query.exec_time

    def get_url(self):
        return 'http://localhost:5000/rcdAnnotations/%d/%d/' % (
                    self.iteration.exp.exp_id, self.iteration.iter_num)

    def get_exec_times_header(self):
        header = ['analysis']
        header.extend(CoreRcd.get_exec_times_header(self))
        return header

    def get_exec_times(self):
        line = [self.queries['rcd'].analysis_time]
        line.extend(CoreRcd.get_exec_times(self))
        return line

    def get_exec_times_display(self):
        v = [PlotDataset(None, 'Analysis')]
        v.extend(CoreRcd.get_exec_times_display(self))
        return v
