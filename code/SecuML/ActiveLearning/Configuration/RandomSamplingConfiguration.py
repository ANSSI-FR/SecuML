## SecuML
## Copyright (C) 2016  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

import ActiveLearningConfFactory
from ActiveLearningConfiguration import ActiveLearningConfiguration
from SecuML.ActiveLearning.QueryStrategies.RandomSampling import RandomSampling

class RandomSamplingConfiguration(ActiveLearningConfiguration):

    def __init__(self, num_annotations):
        self.labeling_method = 'RandomSampling'
        self.batch           = num_annotations

    def getStrategy(self, iteration):
        return RandomSampling(iteration)

    def generateSuffix(self):
        suffix  = ''
        suffix += '__' + str(self.batch)
        return suffix

    @staticmethod
    def fromJson(obj):
        conf = RandomSamplingConfiguration(obj['batch'])
        return conf

    def toJson(self):
        conf = {}
        conf['__type__'] = 'RandomSamplingConfiguration'
        conf['batch']    = self.batch
        return conf

ActiveLearningConfFactory.getFactory().registerClass('RandomSamplingConfiguration',
        RandomSamplingConfiguration)
