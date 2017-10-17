## SecuML
## Copyright (C) 2016-2017  ANSSI
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

# Feature Selection
from SecuML.DimensionReduction.Configuration.FeatureSelection.ChiSquareConfiguration \
        import ChiSquareConfiguration
from SecuML.DimensionReduction.Configuration.FeatureSelection.FclassifConfiguration \
        import FclassifConfiguration
from SecuML.DimensionReduction.Configuration.FeatureSelection.MutualInfoClassifConfiguration \
        import MutualInfoClassifConfiguration
from SecuML.DimensionReduction.Configuration.FeatureSelection.NoneFilterConfiguration \
        import NoneFilterConfiguration
from SecuML.DimensionReduction.Configuration.FeatureSelection.RecursiveFeatureEliminationConfiguration \
        import RecursiveFeatureEliminationConfiguration
from SecuML.DimensionReduction.Configuration.FeatureSelection.VarianceFilterConfiguration \
        import VarianceFilterConfiguration

# Projection
from SecuML.DimensionReduction.Configuration.Projection.PcaConfiguration \
        import PcaConfiguration
from SecuML.DimensionReduction.Configuration.Projection.LdaConfiguration \
        import LdaConfiguration
from SecuML.DimensionReduction.Configuration.Projection.LmnnConfiguration \
        import LmnnConfiguration
from SecuML.DimensionReduction.Configuration.Projection.NcaConfiguration \
        import NcaConfiguration
from SecuML.DimensionReduction.Configuration.Projection.RcaConfiguration \
        import RcaConfiguration
from SecuML.DimensionReduction.Configuration.Projection.ItmlConfiguration \
        import ItmlConfiguration
from SecuML.DimensionReduction.Configuration.Projection.SdmlConfiguration \
        import SdmlConfiguration

# Clustering
from SecuML.Clustering.Configuration.GaussianMixtureConfiguration \
        import GaussianMixtureConfiguration
from SecuML.Clustering.Configuration.KmeansConfiguration \
        import KmeansConfiguration

# Classification
from SecuML.Classification.Configuration.DecisionTreeConfiguration \
        import DecisionTreeConfiguration
from SecuML.Classification.Configuration.GaussianNaiveBayesConfiguration \
        import GaussianNaiveBayesConfiguration
from SecuML.Classification.Configuration.LabelPropagationConfiguration \
        import LabelPropagationConfiguration
from SecuML.Classification.Configuration.LogisticRegressionConfiguration \
        import LogisticRegressionConfiguration
from SecuML.Classification.Configuration.RandomForestConfiguration \
        import RandomForestConfiguration
from SecuML.Classification.Configuration.SssvddConfiguration \
        import SssvddConfiguration
from SecuML.Classification.Configuration.SvcConfiguration \
        import SvcConfiguration

# Active Learning
from SecuML.ActiveLearning.Configuration.AladinConfiguration import AladinConfiguration
from SecuML.ActiveLearning.Configuration.CesaBianchiConfiguration import CesaBianchiConfiguration
from SecuML.ActiveLearning.Configuration.GornitzConfiguration import GornitzConfiguration
from SecuML.ActiveLearning.Configuration.IlabConfiguration import IlabConfiguration
from SecuML.ActiveLearning.Configuration.RandomSamplingConfiguration import RandomSamplingConfiguration
from SecuML.ActiveLearning.Configuration.RareCategoryDetectionConfiguration import RareCategoryDetectionConfiguration
from SecuML.ActiveLearning.Configuration.UncertaintySamplingConfiguration import UncertaintySamplingConfiguration
