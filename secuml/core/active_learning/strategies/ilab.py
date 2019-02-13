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

from secuml.core.active_learning.queries.rcd import RcdQueries
from secuml.core.active_learning.queries.uncertain import UncertainQueries
from secuml.core.data.labels_tools import BENIGN, MALICIOUS

from . import Strategy


class Ilab(Strategy):

    def _set_queries(self):
        self.queries['uncertain'] = UncertainQueries(
                                             self.iteration,
                                             self.iteration.conf.num_uncertain,
                                             label='uncertain')
        # input_checking set to False, because ILAB strategy handles
        # the case where the dataset contains too few families.
        # In this case, random sampling is used instead
        # of rare category detection.
        # When enough families have been discovered with random sampling,
        # rare category detection is then executed.
        self.queries['malicious'] = RcdQueries(self.iteration, MALICIOUS,
                                               0.5, 1, input_checking=False)
        self.queries['benign'] = RcdQueries(self.iteration, BENIGN, 0, 0.5,
                                            input_checking=False)
