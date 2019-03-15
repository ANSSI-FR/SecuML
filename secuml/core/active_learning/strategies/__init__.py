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

import abc

from secuml.core.tools.plots.dataset import PlotDataset


class Strategy(object):

    def __init__(self, iteration):
        self.iteration = iteration
        self.conf = self.iteration.conf
        self.queries = {}
        self._set_queries()

    @abc.abstractmethod
    def _set_queries():
        return

    def generate_queries(self, predictions):
        self.exec_time = 0
        queried_instances = []
        for _, query in self.queries.items():
            query.run(predictions, already_queried=queried_instances)
            queried_instances.extend(query.get_ids())
            self.exec_time += query.exec_time

    def annotate_auto(self):
        for _, query in self.queries.items():
            query.annotate_auto()

    def get_manual_annotations(self):
        for _, query in self.queries.items():
            query.get_manual_annotations()

    def get_exec_times_header(self):
        return ['generate_queries']

    def get_exec_times(self):
        return [self.exec_time]

    def get_exec_times_display(self):
        generate_queries = PlotDataset(None, 'Queries generation')
        generate_queries.set_color('purple')
        return [generate_queries]
