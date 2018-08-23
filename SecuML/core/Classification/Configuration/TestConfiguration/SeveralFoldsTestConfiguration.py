# SecuML
# Copyright (C) 2018  ANSSI
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

from SecuML.core.Classification.CvClassifierDatasets import CvClassifierDatasets
from .TestConfiguration import TestConfiguration


class SeveralFoldsTestConfiguration(TestConfiguration):

    def __init__(self, num_folds, alerts_conf=None, logger=None):
        TestConfiguration.__init__(self, alerts_conf=alerts_conf, logger=logger)
        self.num_folds = num_folds

    def toJson(self):
        conf = TestConfiguration.toJson(self)
        conf['__type__'] = 'SeveralFoldsTestConfiguration'
        conf['num_folds'] = self.num_folds
        return conf

    def generateDatasets(self, classification_conf, instances, test_instances):
        datasets = CvClassifierDatasets(
                            self,
                            classification_conf.families_supervision,
                            classification_conf.sample_weight)
        datasets.generateDatasets(instances, test_instances)
        return datasets
