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

from secuml.core.active_learning.strategies.uncertainty import Uncertainty \
        as CoreUncertainty
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.exp.active_learning.queries.uncertain import UncertainQueries


class Uncertainty(CoreUncertainty):

    def _set_queries(self):
        self.queries['uncertain'] = UncertainQueries(self.iteration,
                                                     self.iteration.conf.batch)

    def get_url(self):
        return 'http://localhost:5000/individualAnnotations/%d/%d/' % (
                    self.iteration.exp.exp_id, self.iteration.iter_num)

    def get_exec_times_header(self):
        header = ['binary_model']
        header.extend(CoreUncertainty.get_exec_times_header(self))
        return header

    def get_exec_times(self):
        line = [self.iteration.update_model.exec_time]
        line.extend(CoreUncertainty.get_exec_times(self))
        return line

    def get_exec_times_display(self):
        binary_model = PlotDataset(None, 'Binary model')
        v = [binary_model]
        v.extend(CoreUncertainty.get_exec_times_display(self))
        return v
