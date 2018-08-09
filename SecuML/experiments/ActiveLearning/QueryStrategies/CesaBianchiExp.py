# SecuML
# Copyright (C) 2017-2018  ANSSI
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

from SecuML.core.ActiveLearning.QueryStrategies.CesaBianchi import CesaBianchi

from . import ActiveLearningStrategyFactoryExp
from .AnnotationQueries.CesaBianchiAnnotationQueriesExp import CesaBianchiAnnotationQueriesExp


class CesaBianchiExp(CesaBianchi):

    def setQueries(self):
        b = self.iteration.conf.b
        num_annotations = self.iteration.conf.batch
        self.annotations = CesaBianchiAnnotationQueriesExp(
            self.iteration, b, num_annotations)


ActiveLearningStrategyFactoryExp.getFactory().registerClass('CesaBianchiExp',
                                                            CesaBianchiExp)
