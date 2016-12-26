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

import os
import config

current_dir = os.path.dirname(os.path.realpath(__file__))

config.INPUTDATA_DIR = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir, 
    config.INPUTDATA_DIR))
config.OUTPUTDATA_DIR = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir,
    config.OUTPUTDATA_DIR))

# Projection
from SecuML.UnsupervisedLearning.Configuration.PcaConfiguration \
        import PcaConfiguration
from SecuML.UnsupervisedLearning.Configuration.LdaConfiguration \
        import LdaConfiguration
from SecuML.UnsupervisedLearning.Configuration.LmnnConfiguration \
        import LmnnConfiguration
from SecuML.UnsupervisedLearning.Configuration.NcaConfiguration \
        import NcaConfiguration
from SecuML.UnsupervisedLearning.Configuration.RcaConfiguration \
        import RcaConfiguration

# Clustering
from SecuML.UnsupervisedLearning.Configuration.GaussianMixtureConfiguration \
        import GaussianMixtureConfiguration
from SecuML.UnsupervisedLearning.Configuration.KmeansConfiguration \
        import KmeansConfiguration

# Classification
from SecuML.SupervisedLearning.Configuration.LogisticRegressionConfiguration \
        import LogisticRegressionConfiguration
from SecuML.SupervisedLearning.Configuration.SvcConfiguration \
        import SvcConfiguration
