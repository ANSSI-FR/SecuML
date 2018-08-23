# SecuML
# Copyright (C) 2017  ANSSI
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

from SecuML.core.ActiveLearning.QueryStrategies.RandomSampling import RandomSampling

from . import ActiveLearningStrategyFactoryExp
from .AnnotationQueries.RandomAnnotationQueriesExp import RandomAnnotationQueriesExp


class RandomSamplingExp(RandomSampling):

    def setQueries(self):
        num_annotations = self.iteration.conf.batch
        self.random_annotations = RandomAnnotationQueriesExp(
            self.iteration, num_annotations)

    def getUrl(self):
        return 'http://localhost:5000/individualAnnotations/%d/%d/' % (
                    self.iteration.experiment.experiment_id,
                    self.iteration.iteration_number)


ActiveLearningStrategyFactoryExp.getFactory().registerClass('RandomSamplingExp',
                                                            RandomSamplingExp)
