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

from secuml.core.active_learning.strategies.ilab import Ilab as CoreIlab
from secuml.core.data.labels_tools import BENIGN, MALICIOUS
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.core.tools.color import get_label_color
from secuml.exp.active_learning.queries.rcd import RcdQueries
from secuml.exp.active_learning.queries.uncertain import UncertainQueries
from secuml.exp.tools.db_tables import IlabExpAlchemy


class Ilab(CoreIlab):

    def _set_queries(self):
        self.queries['uncertain'] = UncertainQueries(
                                             self.iteration,
                                             self.iteration.conf.num_uncertain,
                                             label='uncertain')
        self.queries['malicious'] = RcdQueries(self.iteration, MALICIOUS,
                                               0.5, 1, input_checking=False)
        self.queries['benign'] = RcdQueries(self.iteration, BENIGN, 0, 0.5,
                                            input_checking=False)

    def generate_queries(self, predictions):
        self.exec_time = 0
        queried_instances = []
        ilab_row = IlabExpAlchemy(id=self.iteration.exp.exp_id,
                                  iter=self.iteration.iter_num,
                                  uncertain=None, malicious=None, benign=None)
        for k in ['uncertain', 'malicious', 'benign']:
            query = self.queries[k]
            query.run(predictions, already_queried=queried_instances)
            if k == 'uncertain':
                ilab_row.uncertain = -1
                self.iteration.exp.session.add(ilab_row)
                self.iteration.exp.session.commit()
            else:
                clustering_exp = -1
                if query.clustering_exp is not None:
                    clustering_exp = query.clustering_exp.exp_id
                setattr(ilab_row, k, clustering_exp)
                self.iteration.exp.session.commit()
            queried_instances.extend(query.get_ids())
            self.exec_time += query.exec_time

    def get_url(self):
        return 'http://localhost:5000/ilabAnnotations/%d/%d/' % (
                    self.iteration.exp.exp_id, self.iteration.iter_num)

    def get_exec_times_header(self):
        return ['malicious_queries', 'uncertain_queries', 'benign_queries']

    def get_exec_times(self):
        malicious_time = self.queries['malicious'].analysis_time
        malicious_time += self.queries['malicious'].exec_time
        uncertain_time = self.iteration.update_model.exec_time
        uncertain_time += self.queries['uncertain'].exec_time
        benign_time = self.queries['benign'].analysis_time
        benign_time += self.queries['benign'].exec_time
        return [malicious_time, uncertain_time, benign_time]

    def get_exec_times_display(self):
        uncertain = PlotDataset(None, 'Uncertain Queries')
        malicious = PlotDataset(None, 'Malicious Queries')
        malicious.set_linestyle('dotted')
        malicious.set_color(get_label_color(MALICIOUS))
        benign = PlotDataset(None, 'Benign Queries')
        benign.set_linestyle('dashed')
        benign.set_color(get_label_color(BENIGN))
        return [malicious, uncertain, benign]
