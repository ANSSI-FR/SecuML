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

from SecuML.core.classification.ClassifierDatasets import ClassifierDatasets
from .TestConf import TestConf


class OneFoldTestConf(TestConf):

    def __init__(self, logger, alerts_conf):
        TestConf.__init__(self, logger, alerts_conf)

    def generateDatasets(self, classifier_conf, instances, test_instances):
        datasets = ClassifierDatasets(self, classifier_conf.sample_weight)
        datasets.generateDatasets(instances, test_instances)
        return datasets
