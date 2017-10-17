## SecuML
## Copyright (C) 2017  ANSSI
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

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from SecuML.Classification.Classifier import Classifier

class RandomForest(Classifier):

    def createPipeline(self):
        self.pipeline = Pipeline([
            ('model', RandomForestClassifier(
                n_estimators = self.conf.n_estimators,
                criterion = self.conf.criterion,
                max_features = self.conf.max_features,
                max_depth = self.conf.max_depth,
                min_samples_split = self.conf.min_samples_split,
                min_samples_leaf = self.conf.min_samples_leaf,
                min_weight_fraction_leaf = self.conf.min_weight_fraction_leaf,
                max_leaf_nodes = self.conf.max_leaf_nodes,
                min_impurity_split = self.conf.min_impurity_decrease,
                bootstrap = self.conf.bootstrap,
                oob_score= self.conf.oob_score))])
