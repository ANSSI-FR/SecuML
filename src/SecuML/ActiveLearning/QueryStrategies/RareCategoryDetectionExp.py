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

import json

from AnnotationQueries.RareCategoryDetectionAnnotationQueriesExp import RareCategoryDetectionAnnotationQueriesExp

from QueryStrategy import QueryStrategy
from RareCategoryDetection import RareCategoryDetection

class RareCategoryDetectionExp(RareCategoryDetection):

    def __init__(self, iteration):
        QueryStrategy.__init__(self, iteration)
        multiclass_model   = self.iteration.update_model.models['multiclass']
        multiclass_exp     = self.iteration.update_model.models_exp['multiclass']
        self.all_instances = RareCategoryDetectionAnnotationQueriesExp(self.iteration, 'all', 0, 1,
                                                                       multiclass_model = multiclass_model,
                                                                       multiclass_exp   = multiclass_exp)

    def generateAnnotationQueries(self):
        RareCategoryDetection.generateAnnotationQueries(self)
        self.exportAnnotationsTypes()

    def exportAnnotationsTypes(self):
        clustering_exp = self.all_instances.clustering_exp
        if clustering_exp is not None:
            clustering_exp = clustering_exp.experiment_id
        types = {'all': {'type': self.all_instances.annotations_type,
                         'clustering_exp': clustering_exp
                        }
                }
        filename  = self.iteration.iteration_dir
        filename += 'annotations_types.json'
        with open(filename, 'w') as f:
            json.dump(types, f, indent = 2)
