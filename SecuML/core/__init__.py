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

# Active Learning
from .ActiveLearning.Configuration.AladinConfiguration \
        import AladinConfiguration
from .ActiveLearning.Configuration.CesaBianchiConfiguration \
        import CesaBianchiConfiguration
from .ActiveLearning.Configuration.GornitzConfiguration \
        import GornitzConfiguration
from .ActiveLearning.Configuration.IlabConfiguration \
        import IlabConfiguration
from .ActiveLearning.Configuration.RandomSamplingConfiguration \
        import RandomSamplingConfiguration
from .ActiveLearning.Configuration.RareCategoryDetectionConfiguration \
        import RareCategoryDetectionConfiguration
from .ActiveLearning.Configuration.UncertaintySamplingConfiguration \
        import UncertaintySamplingConfiguration

# Classification
from SecuML.core.Classification.Configuration.DecisionTreeConfiguration \
    import DecisionTreeConfiguration
from SecuML.core.Classification.Configuration.GaussianNaiveBayesConfiguration \
    import GaussianNaiveBayesConfiguration
from SecuML.core.Classification.Configuration.GradientBoostingConfiguration \
    import GradientBoostingConfiguration
from SecuML.core.Classification.Configuration.LabelPropagationConfiguration \
    import LabelPropagationConfiguration
from SecuML.core.Classification.Configuration.LogisticRegressionConfiguration \
    import LogisticRegressionConfiguration
from SecuML.core.Classification.Configuration.RandomForestConfiguration \
    import RandomForestConfiguration
from SecuML.core.Classification.Configuration.SssvddConfiguration \
    import SssvddConfiguration
from SecuML.core.Classification.Configuration.SvcConfiguration \
    import SvcConfiguration

# Clustering
from SecuML.core.Clustering.Configuration.GaussianMixtureConfiguration \
    import GaussianMixtureConfiguration
from SecuML.core.Clustering.Configuration.KmeansConfiguration \
    import KmeansConfiguration

# Feature Selection
from .DimensionReduction.Configuration.FeatureSelection.ChiSquareConfiguration \
    import ChiSquareConfiguration
from .DimensionReduction.Configuration.FeatureSelection.FclassifConfiguration \
    import FclassifConfiguration
from .DimensionReduction.Configuration.FeatureSelection.MutualInfoClassifConfiguration \
    import MutualInfoClassifConfiguration
from .DimensionReduction.Configuration.FeatureSelection.NoneFilterConfiguration \
    import NoneFilterConfiguration
from .DimensionReduction.Configuration.FeatureSelection.RecursiveFeatureEliminationConfiguration \
    import RecursiveFeatureEliminationConfiguration
from .DimensionReduction.Configuration.FeatureSelection.VarianceFilterConfiguration \
    import VarianceFilterConfiguration

# Projection
from .DimensionReduction.Configuration.Projection.PcaConfiguration \
    import PcaConfiguration
from .DimensionReduction.Configuration.Projection.LdaConfiguration \
    import LdaConfiguration
from .DimensionReduction.Configuration.Projection.LmnnConfiguration \
    import LmnnConfiguration
from .DimensionReduction.Configuration.Projection.NcaConfiguration \
    import NcaConfiguration
from .DimensionReduction.Configuration.Projection.RcaConfiguration \
    import RcaConfiguration
from .DimensionReduction.Configuration.Projection.ItmlConfiguration \
    import ItmlConfiguration
from .DimensionReduction.Configuration.Projection.SdmlConfiguration \
    import SdmlConfiguration
