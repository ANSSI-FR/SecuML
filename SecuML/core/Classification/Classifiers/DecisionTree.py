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

from sklearn import tree
from sklearn.pipeline import Pipeline

from SecuML.core.Classification.Classifier import Classifier


class DecisionTree(Classifier):

    def createPipeline(self):
        self.pipeline = Pipeline([
            ('model', tree.DecisionTreeClassifier(
                criterion=self.conf.criterion,
                splitter=self.conf.splitter,
                max_depth=self.conf.max_depth,
                min_samples_split=self.conf.min_samples_split,
                min_samples_leaf=self.conf.min_samples_leaf,
                min_weight_fraction_leaf=self.conf.min_weight_fraction_leaf,
                max_features=self.conf.max_features,
                max_leaf_nodes=self.conf.max_leaf_nodes,
                min_impurity_decrease=self.conf.min_impurity_decrease))])
