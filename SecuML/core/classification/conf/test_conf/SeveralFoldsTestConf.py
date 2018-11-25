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

from SecuML.core.classification.CvClassifierDatasets import CvClassifierDatasets
from SecuML.core.Conf import exportFieldMethod

from .TestConf import TestConf


class SeveralFoldsTestConf(TestConf):

    def __init__(self, logger, alerts_conf, num_folds):
        TestConf.__init__(self, logger, alerts_conf)
        self.num_folds = num_folds

    def fieldsToExport(self):
        fields = TestConf.fieldsToExport(self)
        fields.extend([('num_folds', exportFieldMethod.primitive)])
        return fields

    def generateDatasets(self, classifier_conf, instances, test_instances):
        datasets = CvClassifierDatasets(self,
                                        classifier_conf.families_supervision,
                                        classifier_conf.sample_weight)
        datasets.generateDatasets(instances)
        return datasets
