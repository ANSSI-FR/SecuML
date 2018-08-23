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

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from SecuML.core.DimensionReduction.Algorithms.FeatureSelection.RecursiveFeatureElimination \
    import RecursiveFeatureElimination
from SecuML.core.DimensionReduction.Configuration \
        import DimensionReductionConfFactory

from .SemiSupervisedFeatureSelectionConfiguration \
        import SemiSupervisedFeatureSelectionConfiguration


class RecursiveFeatureEliminationConfiguration(SemiSupervisedFeatureSelectionConfiguration):

    def __init__(self, model, step, num_components=None,
                 families_supervision=None, logger=None):
        SemiSupervisedFeatureSelectionConfiguration.__init__(
                                     self,
                                     RecursiveFeatureElimination,
                                     num_components=num_components,
                                     families_supervision=families_supervision,
                                     logger=logger)
        self.model = model
        self.step = step

    def generateSuffix(self):
        suffix = SemiSupervisedFeatureSelectionConfiguration.generateSuffix(
            self)
        suffix += '_step' + str(self.step)
        return suffix

    @staticmethod
    def fromJson(obj, logger=None):
        conf = RecursiveFeatureEliminationConfiguration(
            None,
            obj['step'],
            num_components=obj['num_components'],
            families_supervision=obj['families_supervision'],
            logger=logger)
        return conf

    def toJson(self):
        conf = SemiSupervisedFeatureSelectionConfiguration.toJson(self)
        conf['__type__'] = 'RecursiveFeatureEliminationConfiguration'
        conf['step'] = self.step
        return conf

    @staticmethod
    def generateParamsFromArgs(args):
        params = SemiSupervisedFeatureSelectionConfiguration.generateParamsFromArgs(
            args)
        params['step'] = args.step
        if args.model == 'LogisticRegression':
            model = LogisticRegression()
        elif args.model == 'Svc':
            model = SVC(kernel='linear')
        elif args.model == 'DecisionTree':
            model = DecisionTreeClassifier()
        elif args.model == 'RandomForest':
            model = RandomForestClassifier()
        params['model'] = model
        return params

    @staticmethod
    def generateParser(parser):
        SemiSupervisedFeatureSelectionConfiguration.generateParser(parser)
        parser.add_argument('--step',
                            type=int,
                            default=1)
        parser.add_argument('--model',
                            type=str,
                            choices=['LogisticRegression', 'Svc',
                                     'DecisionTree', 'RandomForest'],
                            default='LogisticRegression')


DimensionReductionConfFactory.getFactory().registerClass(
                        'RecursiveFeatureEliminationConfiguration',
                        RecursiveFeatureEliminationConfiguration)
