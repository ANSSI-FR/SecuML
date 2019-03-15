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

from . import Queries


class RandomQueries(Queries):

    def __init__(self, iteration, num_annotations):
        Queries.__init__(self, iteration)
        self.num_annotations = num_annotations

    def run_models(self):
        return

    def generate_queries(self, already_queried=None):
        selection = self.predictions.get_random(self.num_annotations,
                                                already_queried)
        for prediction in selection:
            query = self.generate_query(prediction.instance_id,
                                        prediction.proba, None, None)
            self.add_query(query)
