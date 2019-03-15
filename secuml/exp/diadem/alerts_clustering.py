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

from secuml.exp.clustering import ClusteringExperiment


class AlertsClusteringExp(ClusteringExperiment):

    def __init__(self, exp_conf, diadem_exp_id, create=True, session=None):
        ClusteringExperiment.__init__(self, exp_conf, create=create,
                                      session=session)
        self.diadem_exp_id = diadem_exp_id

    def add_to_db(self):
        ClusteringExperiment.add_to_db(self)
        # add the AlertsClustering exp. to the DB.
        from secuml.exp.diadem import add_diadem_exp_to_db
        add_diadem_exp_to_db(self.session, self.exp_id, None, 'alerts')
