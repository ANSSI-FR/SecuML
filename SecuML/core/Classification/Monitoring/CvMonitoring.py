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

from .FamiliesMonitoring import FamiliesMonitoring
from .TrainingMonitoring import TrainingMonitoring


class CvMonitoring(TrainingMonitoring):

    def __init__(self, conf, num_folds):
        TrainingMonitoring.__init__(self, conf)
        self.monitoring_type = 'cv'
        self.num_folds = num_folds

    def initFamiliesMonitoring(self, datasets):
        self.families_monitoring = FamiliesMonitoring(datasets, 'train', True)
