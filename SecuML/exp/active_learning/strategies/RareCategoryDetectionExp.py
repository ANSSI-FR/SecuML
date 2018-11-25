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

import json
import os.path as path

from SecuML.core.active_learning.strategies.Strategy import Strategy
from SecuML.core.active_learning.strategies.RareCategoryDetection \
        import RareCategoryDetection

from . import ActiveLearningStrategyFactoryExp
from .queries.RareCategoryDetectionQueriesExp \
        import RareCategoryDetectionQueriesExp


class RareCategoryDetectionExp(RareCategoryDetection):

    def __init__(self, iteration):
        Strategy.__init__(self, iteration)
        self.all_instances = RareCategoryDetectionQueriesExp(self.iteration,
                                                             'all', 0, 1)

    def generateQueries(self):
        RareCategoryDetection.generateQueries(self)
        self.exportAnnotationsTypes()

    def exportAnnotationsTypes(self):
        clustering_exp = self.all_instances.clustering_exp
        if clustering_exp is not None:
            clustering_exp = clustering_exp.experiment_id
        types = {'all': {'type': self.all_instances.annotations_type,
                         'clustering_exp': clustering_exp
                         }
                 }
        filename = path.join(self.iteration.iteration_dir,
                             'annotations_types.json')
        with open(filename, 'w') as f:
            json.dump(types, f, indent=2)

    def getUrl(self):
        return 'http://localhost:5000/rareCategoryDetectionAnnotations/%d/%d/' % (
                    self.iteration.experiment.experiment_id,
                    self.iteration.iteration_number)


ActiveLearningStrategyFactoryExp.getFactory().registerClass(
                                                    'RareCategoryDetectionExp',
                                                     RareCategoryDetectionExp)
