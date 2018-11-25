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

from SecuML.core.classification.conf.ClassificationConf \
        import ClassificationConf
from SecuML.core.Conf import Conf
from SecuML.core.Conf import exportFieldMethod


class RareCategoryDetectionStrategy(Conf):

    def __init__(self, classification_conf, cluster_strategy, num_annotations,
                 cluster_weights, logger):
        Conf.__init__(self, logger)
        self.classification_conf = classification_conf
        self.cluster_strategy = cluster_strategy
        self.num_annotations = num_annotations
        self.cluster_weights = cluster_weights

    def get_exp_name(self):
        name = self.classification_conf.get_exp_name()
        name += '__numAnnotations_%d' % self.num_annotations
        return name

    def fieldsToExport(self):
        return [('classification_conf', exportFieldMethod.obj),
                ('cluster_strategy', exportFieldMethod.primitive),
                ('num_annotations', exportFieldMethod.primitive),
                ('cluster_weights', exportFieldMethod.primitive)]

    @staticmethod
    def from_json(obj, logger):
        classif_conf = ClassificationConf.from_json(obj['classification_conf'],
                                                    logger)
        return RareCategoryDetectionStrategy(classif_conf,
                                             obj['cluster_strategy'],
                                             obj['num_annotations'],
                                             obj['cluster_weights'],
                                             logger)
