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

import time

from .monitoring.labels import LabelsMonitoring
from .monitoring.suggestions_accuracy import SuggestionsAccuracy
from .queries import NoAnnotationBudget
from .update_model import UpdateModel
from secuml.core.tools.core_exceptions import SecuMLcoreException


class NoAnnotationAdded(SecuMLcoreException):

    def __str__(self):
        return 'The iteration has not added any annotation.'


class NoUnlabeledDataLeft(SecuMLcoreException):

    def __str__(self):
        return 'There remains no unlabeled instances to be annotated.'


class Iteration(object):

    def __init__(self, conf, iter_num, datasets=None, prev_iter=None,
                 budget=None):
        self.prev_iter = prev_iter
        self.conf = conf
        self.datasets = datasets
        self.budget = budget
        self.iter_num = iter_num

    def set_query_strategy(self):
        self.strategy = self.conf.get_strategy()(self)

    def run(self):
        self.check_unlabeled_data()
        self.set_query_strategy()
        self.conf.logger.info('Start iteration n°%d' % self.iter_num)
        start = time.time()
        self.init_computations()
        self.update_model()
        self.generate_queries()
        self.answer_queries()
        self.global_execution_time = time.time() - start
        self.conf.logger.info('End iteration n°%d' % self.iter_num)
        self.conf.logger.info('Iteration n°%d: %f sec' % (
                                                   self.iter_num,
                                                   self.global_execution_time))
        return self.budget

    def check_unlabeled_data(self):
        unlabeled_data = self.datasets.get_unlabeled_instances()
        if unlabeled_data.num_instances() == 0:
            raise NoUnlabeledDataLeft()

    def generate_queries(self, predictions):
        self.strategy.generate_queries(predictions)

    def init_computations(self):
        if self.prev_iter is not None:
            self.prev_iter.final_computations()
        self.labels_monitoring = LabelsMonitoring(self)
        self.labels_monitoring.generate()
        self.suggestions_accuracy = SuggestionsAccuracy(self)

    def final_computations(self):
        if not self.conf.auto:
            try:
                self.update_annotated_instances()
            except (NoAnnotationBudget) as e:
                self.conf.logger.info(e)
                pass
        self.end_monitoring()
        self.check_new_annotations()

    def end_monitoring(self):
        self.suggestions_accuracy.generate()

    def update_model(self):
        self.update_model = UpdateModel(self)
        self.update_model.execute()

    def answer_queries(self):
        try:
            self.datasets.new_annotations = False
            self.strategy.annotate_auto()
        except (NoAnnotationBudget) as e:
            self.conf.logger.info(e)
            pass

    # Raise the exception NoAnnotationAdded if no new annotation
    # has been added during the current iteration
    def check_new_annotations(self):
        if not self.datasets.new_annotations:
            raise NoAnnotationAdded()
