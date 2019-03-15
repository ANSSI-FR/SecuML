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
from secuml.core.tools.color import red
from secuml.core.tools.plots.barplot import BarPlot
from secuml.core.tools.plots.dataset import PlotDataset
from secuml.exp.tools.db_tables import FeaturesAlchemy


NUM_COEFF_EXPORT = 15


class Coefficients(CoefficientsCore):

    def __init__(self, num_folds, features, classifier_conf, session):
        CoefficientsCore.__init__(self, num_folds, features)
        self.classifier_conf = classifier_conf
        self.session = session

    def display(self, directory):
        CoefficientsCore.display(self, directory)
        self.to_barplot(directory)

    def to_barplot(self, directory):
        head_coeff = self.coef_summary.head(n=NUM_COEFF_EXPORT)
        coefficients = list(head_coeff['mean'])
        features_ids = head_coeff.index
        tooltip_data = []
        user_ids = []
        for feature_id in features_ids:
            query = self.session.query(FeaturesAlchemy)
            query = query.filter(FeaturesAlchemy.id == int(feature_id))
            row = query.one()
            tooltip_data.append(row.name)
            user_ids.append(row.user_id)
        barplot = BarPlot(user_ids)
        dataset = PlotDataset(coefficients, None)
        score = self.classifier_conf.get_feature_importance()
        if score == 'weight':
            dataset.set_color(red)
        barplot.add_dataset(dataset)
        out_filename = path.join(directory, 'coeff_barplot.json')
        return barplot.export_to_json(out_filename, tooltip_data=tooltip_data)
