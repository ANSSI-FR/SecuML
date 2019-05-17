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

import os.path as path

from secuml.core.classif.monitoring.interp.coeff import Coefficients \
        as CoefficientsCore
from secuml.core.classif.monitoring.interp.coeff import ClassCoefficients \
        as ClassCoefficientsCore
from secuml.core.tools.color import blue, red
from secuml.core.tools.plots.barplot import BarPlot
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.exp.tools.db_tables import FeaturesAlchemy


NUM_COEFF_EXPORT = 15


class ClassCoefficients(ClassCoefficientsCore):

    def __init__(self, exp, classifier_conf, features_info, class_label,
                 num_folds=1):
        ClassCoefficientsCore.__init__(self, features_info, class_label,
                                       num_folds=num_folds)
        self.exp = exp
        self.classifier_conf = classifier_conf

    def to_barplot(self, directory):
        head_coeff = self.coef_summary.head(n=NUM_COEFF_EXPORT)
        coefficients = head_coeff['mean'].values
        features_ids = list(head_coeff.index)
        features_names = []
        user_ids = []
        for feature_id in features_ids:
            query = self.exp.session.query(FeaturesAlchemy)
            query = query.filter(FeaturesAlchemy.id == int(feature_id))
            row = query.one()
            features_names.append(row.name)
            user_ids.append(row.user_id)
        barplot = BarPlot(user_ids)
        dataset = PlotDataset(coefficients, None)
        score = self.classifier_conf.get_feature_importance()
        if score == 'weight':
            dataset.set_color(red)
        else:
            dataset.set_color(blue)
        barplot.add_dataset(dataset)
        if self.class_label is None:
            out_filename = 'coeff_barplot.json'
        else:
            out_filename = 'coeff_barplot_%s.json' % self.class_label
        return barplot.export_to_json(path.join(directory, out_filename),
                                      tooltip_data=features_names)

    def display(self, directory):
        ClassCoefficientsCore.display(self, directory)
        self.to_barplot(directory)


class Coefficients(CoefficientsCore):

    def __init__(self, exp, classifier_conf, class_labels, num_folds=1):
        features_info = exp.exp_conf.features_conf.info
        self.exp = exp
        self.classifier_conf = classifier_conf
        CoefficientsCore.__init__(self, features_info, class_labels,
                                  num_folds=num_folds)

    def _init_class_coefficients(self, features_info, num_folds):
        if self.class_labels is None:
            self.coefficients = ClassCoefficients(self.exp,
                                                  self.classifier_conf,
                                                  features_info, None,
                                                  num_folds=num_folds)
        else:
            self.coefficients = {label: ClassCoefficients(self.exp,
                                                          self.classifier_conf,
                                                          features_info, label,
                                                          num_folds=num_folds)
                                 for label in self.class_labels}
