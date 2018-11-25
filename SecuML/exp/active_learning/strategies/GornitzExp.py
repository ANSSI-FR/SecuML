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

from SecuML.core.active_learning.strategies.Gornitz import Gornitz

from . import ActiveLearningStrategyFactoryExp
from .queries.GornitzQueriesExp import GornitzQueriesExp


class GornitzExp(Gornitz):

    def setQueries(self):
        num_annotations = self.iteration.conf.batch
        self.annotations = GornitzQueriesExp(self.iteration, num_annotations)

    def getUrl(self):
        return 'http://localhost:5000/individualAnnotations/%d/%d/' % (
                    self.iteration.experiment.experiment_id,
                    self.iteration.iteration_number)


ActiveLearningStrategyFactoryExp.getFactory().registerClass('GornitzExp',
                                                            GornitzExp)
