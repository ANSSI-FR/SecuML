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

from . import ActiveLearningConfFactory
from .ActiveLearningConf import ActiveLearningConf
from .RareCategoryDetectionStrategy import RareCategoryDetectionStrategy

from SecuML.core.active_learning.strategies.RareCategoryDetection \
        import RareCategoryDetection
from SecuML.core.classification.conf.ClassificationConf \
        import ClassificationConf
from SecuML.core.Conf import exportFieldMethod


class RareCategoryDetectionConf(ActiveLearningConf):

    def __init__(self, auto, budget, rcd_conf, multiclass_model_conf,
                 validation_conf, logger):
        ActiveLearningConf.__init__(self, auto, budget, validation_conf,
                                    {'multiclass': multiclass_model_conf},
                                    logger)
        self.query_strategy = 'RareCategoryDetection'
        self.rcd_conf = rcd_conf

    def getStrategy(self, iteration):
        return RareCategoryDetection(iteration)

    def get_exp_name(self):
        name = ActiveLearningConf.get_exp_name(self)
        name += '__RCD_%s' % self.rcd_conf.get_exp_name()
        return name

    @staticmethod
    def from_json(obj, logger):
        validation_conf = ActiveLearningConf.validation_conf_from_json(obj,
                                                                       logger)
        multiclass_model_conf = ClassificationConf.from_json(
                                               obj['models_conf']['multiclass'],
                                               logger)
        rcd_conf = RareCategoryDetectionStrategy.from_json(obj['rcd_conf'],
                                                           logger)
        return RareCategoryDetectionConf(obj['auto'], obj['budget'], rcd_conf,
                                         multiclass_model_conf, validation_conf,
                                         logger)

    def fieldsToExport(self):
        fields = ActiveLearningConf.fieldsToExport(self)
        fields.extend([('rcd_conf', exportFieldMethod.obj)])
        return fields

    @staticmethod
    def generateParser(parser):
        al_group = ActiveLearningConf.generateParser(parser,
                                                     classifier_conf=True,
                                                     binary=False)
        al_group.add_argument('--num-annotations',
                              type=int,
                              default=100,
                              help='Number of instances queried '
                                   'for each family.')
        al_group.add_argument('--cluster-strategy',
                              default='center_anomalous')

    @staticmethod
    def fromArgs(args, logger):
        multiclass_conf = ActiveLearningConf.multiclassModelConfFromArgs(args,
                                                                       logger)
        rcd_conf = RareCategoryDetectionStrategy(multiclass_conf,
                                                 args.cluster_strategy,
                                                 args.num_annotations,
                                                 'uniform',
                                                 logger)
        validation_conf = ActiveLearningConf.validation_conf_from_args(args,
                                                                       logger)
        return RareCategoryDetectionConf(args.auto, args.budget, rcd_conf,
                                         multiclass_conf, validation_conf,
                                         logger)


ActiveLearningConfFactory.getFactory().registerClass(
                                            'RareCategoryDetectionConf',
                                            RareCategoryDetectionConf)
