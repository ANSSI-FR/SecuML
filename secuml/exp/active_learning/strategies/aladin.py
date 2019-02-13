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

from secuml.core.active_learning.strategies.aladin import Aladin as CoreAladin
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.exp.active_learning.queries.aladin import AladinQueries


class Aladin(CoreAladin):

    def _set_queries(self):
        self.queries['aladin'] = AladinQueries(self.iteration, self.conf)

    def get_url(self):
        return 'http://localhost:5000/individualAnnotations/%d/%d/' % (
                    self.iteration.exp.exp_id, self.iteration.iter_num)

    def get_exec_times_header(self):
        header = ['logistic_regression', 'naive_bayes']
        header.extend(CoreAladin.get_exec_times_header(self))
        return header

    def get_exec_times(self):
        queries = self.queries['aladin']
        line = [queries.lr_time, queries.nb_time]
        line.extend(CoreAladin.get_exec_times(self))
        return line

    def get_exec_times_display(self):
        lr = PlotDataset(None, 'Logistic Regression')
        lr.set_linestyle('dotted')
        nb = PlotDataset(None, 'Naive Bayes')
        nb.set_linestyle('dashed')
        v = [lr, nb]
        v.extend(CoreAladin.get_exec_times_display(self))
        return v
