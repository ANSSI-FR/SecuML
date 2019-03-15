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

from .iteration import Iteration
from .iteration import NoAnnotationAdded
from .iteration import NoUnlabeledDataLeft


class ActiveLearning(object):

    def __init__(self, conf, datasets):
        self.conf = conf
        self.datasets = datasets
        self.budget = self.conf.budget
        self.iter_num = 1
        self.current_budget = self.budget
        self.prev_iter = None
        self.curr_iter = None

    def run_iterations(self, output_dir=None):
        while True:
            try:
                self.run_next_iter(output_dir)
            except (NoAnnotationAdded, NoUnlabeledDataLeft) as e:
                self.conf.logger.info(e)
                break

    def run_next_iter(self, output_dir=None):
        self.curr_iter = Iteration(self.conf,
                                   self.iter_num,
                                   datasets=self.datasets,
                                   prev_iter=self.prev_iter,
                                   budget=self.current_budget)
        self.current_budget = self.curr_iter.run()
        self.iter_num += 1
        self.curr_iter.prev_iter = None
        self.prev_iter = self.curr_iter
