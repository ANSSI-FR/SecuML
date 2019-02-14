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

from sklearn.externals import joblib
import os.path as path

from .interp.coeff import Coefficients
from .perf import PerformanceMonitoring
from .prediction import PredictionsMonitoring


class TrainMonitoring(object):

    def __init__(self, conf, exec_time):
        self.conf = conf
        self.exec_time = exec_time
        self.monitoring_type = 'train'
        self.num_folds = 1
        self.interpretation = self.conf.is_interpretable()

    def init(self, features_ids):
        self.performance = PerformanceMonitoring(self.num_folds, self.conf)
        self.predictions = PredictionsMonitoring(self.conf, True)
        self.coefficients = None
        if self.interpretation:
            self.coefficients = Coefficients(self.num_folds, features_ids)

    def add_fold(self, fold_id, predictions, pipeline):
        self.performance.add_fold(fold_id, predictions)
        self.predictions.add_fold(predictions)
        self.pipeline = pipeline
        if self.interpretation:
            coefs = self.conf.get_coefs(self.pipeline.named_steps['model'])
            self.coefficients.add_fold(fold_id, coefs)

    def final_computations(self):
        self.performance.final_computations()
        self.predictions.final_computations()
        if self.interpretation:
            self.coefficients.final_computations()

    def display(self, directory):
        self.final_computations()
        self.performance.display(directory)
        self.predictions.display(directory)
        joblib.dump(self.pipeline, path.join(directory, 'model.out'))
        if self.interpretation:
            self.coefficients.display(directory)
