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

import os
from . import config

current_dir = os.path.dirname(os.path.realpath(__file__))

config.INPUTDATA_DIR = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir,
                                                    config.INPUTDATA_DIR))
config.OUTPUTDATA_DIR = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir,
                                                     config.OUTPUTDATA_DIR))

# Active Learning
from SecuML.experiments.ActiveLearning.QueryStrategies.AladinExp import AladinExp
from SecuML.experiments.ActiveLearning.QueryStrategies.CesaBianchiExp import CesaBianchiExp
from SecuML.experiments.ActiveLearning.QueryStrategies.GornitzExp import GornitzExp
from SecuML.experiments.ActiveLearning.QueryStrategies.IlabExp import IlabExp
from SecuML.experiments.ActiveLearning.QueryStrategies.RandomSamplingExp import RandomSamplingExp
from SecuML.experiments.ActiveLearning.QueryStrategies.RareCategoryDetectionExp import RareCategoryDetectionExp
from SecuML.experiments.ActiveLearning.QueryStrategies.UncertaintySamplingExp import UncertaintySamplingExp
