# SecuML
# Copyright (C) 2016-2019  ANSSI
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

from decimal import Decimal
import json
import os.path as path
import pandas as pd
from scipy.sparse.base import spmatrix
from sklearn.feature_selection import chi2
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import mutual_info_classif
from sklearn.utils.sparsefuncs import mean_variance_axis

from secuml.core.data.features import FeatureType
from secuml.core.tools.matrix import sort_data_frame


class ScoreValueRank(object):

    def __init__(self, value, pvalue):
        self.value = value
        self.pvalue = pvalue
        self.rank = None

    def set_rank(self, rank):
        self.rank = rank

    def to_json(self):
        value = '%.2f' % self.value
        pvalue = None if self.pvalue is None else '%.2E' % Decimal(self.pvalue)
        return {'value': value, 'pvalue': pvalue, 'rank': self.rank + 1}


class FeatureScoring(object):

    def __init__(self, feature_id, scores, scoring_func):
        self.feature_id = feature_id
        self._set_scores(scores, scoring_func)

    def set_rank(self, func, rank):
        self.scores[func].set_rank(rank)

    def export(self, output_dir):
        to_export = {}
        for func, score_value_rank in self.scores.items():
            to_export[func] = score_value_rank.to_json()
        output_filename = path.join(output_dir, str(self.feature_id),
                                    'scores.json')
        with open(output_filename, 'w') as f:
            json.dump(to_export, f, indent=2)

    def _set_scores(self, scores, scoring_func):
        self.scores = {}
        for func, has_pvalue in scoring_func:
            row = scores.loc[self.feature_id]
            value = row[func]
            pvalue = None
            if has_pvalue:
                pvalue = row['_'.join([func, 'pvalues'])]
            self.scores[func] = ScoreValueRank(value, pvalue)


class FeaturesScoring(object):

    def __init__(self, instances, multiclass):
        self.instances = instances
        self.multiclass = multiclass
        self.annotated_instances = instances.get_annotated_instances()
        self._set_scoring_func()

    def compute(self):
        self._compute_scores()
        self._compute_features_scoring_ranking()

    def _set_scoring_func(self):
        self.scoring_func = [('variance', False)]
        if self.annotated_instances.num_instances() > 0:
            self.scoring_func.append(('f_classif', True))
            self.scoring_func.append(('mutual_info_classif', False))
            if self.instances.features.all_positives():
                self.scoring_func.append(('chi2', True))

    def _compute_scores(self):
        scores_dict = {}
        for func, has_pvalue in self.scoring_func:
            scores, p_values = self.compute_scoring_func(func)
            scores_dict[func] = scores
            if has_pvalue:
                scores_dict['_'.join([func, 'pvalues'])] = p_values
        self.scores = pd.DataFrame(scores_dict,
                                   index=self.instances.features.info.ids)

    def _compute_features_scoring_ranking(self):
        self.features_scores = {}
        for i, feature_id in enumerate(self.instances.features.info.ids):
            # Store values / pvalues
            self.features_scores[feature_id] = FeatureScoring(
                                                            feature_id,
                                                            self.scores,
                                                            self.scoring_func)
        # Store ranks
        for func, _ in self.scoring_func:
            sort_data_frame(self.scores, func, False, True)
            for rank, feature_id in enumerate(self.scores.index.values):
                self.features_scores[feature_id].set_rank(func, rank)

    def export(self, output_dir):
        self.scores.to_csv(path.join(output_dir, 'scores.csv'),
                           index_label='features_ids')
        for _, feature_scores in self.features_scores.items():
            feature_scores.export(output_dir)

    def compute_scoring_func(self, func):
        if func == 'variance':
            features = self.instances.features.get_values()
            annotations = self.instances.annotations.get_labels()
            if isinstance(features, spmatrix):
                variance = mean_variance_axis(features, axis=0)[1]
            else:
                variance = features.var(axis=0)
            return variance, None

        features = self.annotated_instances.features.get_values()
        annotations = self.annotated_instances.annotations.get_supervision(
                                                               self.multiclass)
        if func == 'f_classif':
            return f_classif(features, annotations)
        elif func == 'mutual_info_classif':
            if isinstance(features, spmatrix):
                discrete_indexes = True
            else:
                features_types = self.instances.features.info.types
                discrete_indexes = [i for i, t in enumerate(features_types)
                                    if t == FeatureType.binary]
                if not discrete_indexes:
                    discrete_indexes = False
            return (mutual_info_classif(features, annotations,
                                        discrete_features=discrete_indexes),
                    None)
        elif func == 'chi2':
            return chi2(features, annotations)
        else:
            assert(False)
