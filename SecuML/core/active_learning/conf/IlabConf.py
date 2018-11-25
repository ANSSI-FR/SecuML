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

from SecuML.core.active_learning.strategies.Ilab import Ilab
from SecuML.core.classification.conf.ClassificationConf \
        import ClassificationConf
from SecuML.core.classification.conf.hyperparam_conf.HyperparamOptimConf \
        import HyperparamOptimConf
from SecuML.core.classification.conf.hyperparam_conf.RocAucConf \
        import RocAucConf
from SecuML.core.classification.conf.LogisticRegressionConf \
        import LogisticRegressionConf
from SecuML.core.classification.conf.test_conf.UnlabeledLabeledConf \
        import UnlabeledLabeledConf
from SecuML.core.Conf import exportFieldMethod


def rcdConf(args, logger):
    hyperparams_optim_conf = HyperparamOptimConf(4, -1, RocAucConf(logger),
                                                 logger)
    multiclass_conf = LogisticRegressionConf(False, True, 'liblinear',
                                            hyperparams_optim_conf, logger)
    classif_conf = ClassificationConf(multiclass_conf,
                                      UnlabeledLabeledConf(logger, None),
                                      logger)
    return RareCategoryDetectionStrategy(classif_conf, args.cluster_strategy,
                                         args.num_annotations, 'uniform',
                                         logger)


class IlabConf(ActiveLearningConf):

    def __init__(self, auto, budget, rcd_conf, num_uncertain, eps,
                 binary_model_conf, validation_conf, logger):
        ActiveLearningConf.__init__(self, auto, budget, validation_conf,
                                    {'binary': binary_model_conf},
                                    logger)
        self.query_strategy = 'Ilab'
        self.eps = eps
        self.num_uncertain = num_uncertain
        self.rcd_conf = rcd_conf

    def getStrategy(self, iteration):
        return Ilab(iteration)

    def get_exp_name(self):
        name = ActiveLearningConf.get_exp_name(self)
        name += '__RCD_%s' % self.rcd_conf.get_exp_name()
        name += '__numUnsure_%d' % self.num_uncertain
        return name

    def fieldsToExport(self):
        fields = ActiveLearningConf.fieldsToExport(self)
        fields.extend([('eps', exportFieldMethod.primitive),
                       ('num_uncertain', exportFieldMethod.primitive),
                       ('rcd_conf', exportFieldMethod.obj)])
        return fields

    @staticmethod
    def generateParser(parser):
        al_group = ActiveLearningConf.generateParser(parser,
                                                     classifier_conf=True)
        al_group.add_argument('--num-uncertain',
                              type=int,
                              default=10,
                              help='Number of instances queried close to the '
                                   'decision boundary.')
        al_group.add_argument('--num-annotations',
                              type=int,
                              default=45,
                              help='Number of instances queried for each '
                                   'family.')
        al_group.add_argument('--cluster-strategy',
                              default='center_anomalous')

    @staticmethod
    def fromArgs(args, logger):
        rcd_conf = rcdConf(args, logger)
        binary_model_conf = ActiveLearningConf.binaryModelConfFromArgs(args,
                                                                       logger)
        validation_conf = ActiveLearningConf.validation_conf_from_args(args,
                                                                       logger)
        return IlabConf(args.auto, args.budget, rcd_conf, args.num_uncertain,
                        0.49, binary_model_conf, validation_conf, logger)

    @staticmethod
    def from_json(obj, logger):
        validation_conf = ActiveLearningConf.validation_conf_from_json(obj,
                                                                       logger)
        rcd_conf = RareCategoryDetectionStrategy.from_json(obj['rcd_conf'],
                                                           logger)
        binary_model_conf = ClassificationConf.from_json(
                                                obj['models_conf']['binary'],
                                                logger)
        conf = IlabConf(obj['auto'], obj['budget'], rcd_conf,
                        obj['num_uncertain'], obj['eps'], binary_model_conf,
                        validation_conf, logger)
        return conf


ActiveLearningConfFactory.getFactory().registerClass('IlabConf', IlabConf)
